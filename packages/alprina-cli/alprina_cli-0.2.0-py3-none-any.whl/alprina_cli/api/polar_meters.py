"""
Polar Meter Integration for Usage-Based Billing
Reports credit consumption to Polar for automatic billing
"""
import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PolarMeterService:
    """Report usage to Polar meters for billing"""

    POLAR_API_URL = "https://api.polar.sh"
    POLAR_ACCESS_TOKEN = os.getenv("POLAR_ACCESS_TOKEN") or os.getenv("POLAR_API_TOKEN")

    # Credit costs for different operations
    CREDIT_COSTS = {
        # Scans - start simple (all = 1 credit)
        "scan_basic": 1,
        "scan_standard": 1,  # Can adjust later: 5 credits
        "scan_deep": 1,      # Can adjust later: 10 credits
        "scan_red_team": 1,
        "scan_blue_team": 1,
        "scan_owasp": 1,

        # Future features (commented for now)
        # "chat_query": 0.5,
        # "chat_analysis": 2,
        # "report_html": 1,
        # "report_pdf": 2,
        # "api_call": 0.1,
    }

    @classmethod
    async def report_credit_usage(
        cls,
        external_customer_id: str,
        credits: int,
        operation: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Report credit consumption to Polar meter using Events API.

        Args:
            external_customer_id: Your internal customer ID (email or user_id)
            credits: Number of credits consumed
            operation: What operation consumed credits (e.g., "scan_basic")
            metadata: Additional context (optional)

        Returns:
            True if successfully reported, False otherwise
        """
        if not cls.POLAR_ACCESS_TOKEN:
            logger.error("POLAR_ACCESS_TOKEN not set")
            return False

        if not external_customer_id:
            logger.error("No external_customer_id provided")
            return False

        # Prepare event payload (matches Polar SDK format)
        event_metadata = {
            "credits": credits,  # This field is summed by meter
            "operation": operation,
        }

        # Add optional metadata
        if metadata:
            event_metadata.update(metadata)

        payload = {
            "events": [
                {
                    "name": "credit_consumed",  # Must match meter event name filter
                    "external_customer_id": external_customer_id,  # Your customer ID (snake_case!)
                    "metadata": event_metadata
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {cls.POLAR_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        try:
            # Send to Polar Events Ingest API
            response = requests.post(
                f"{cls.POLAR_API_URL}/v1/events/ingest",
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code in [200, 201, 204]:
                logger.info(f"✅ Reported {credits} credits to Polar for {operation} (customer: {external_customer_id})")
                return True
            else:
                logger.error(f"❌ Polar API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to report to Polar: {str(e)}")
            return False

    @classmethod
    def get_operation_cost(cls, operation: str) -> int:
        """Get credit cost for an operation"""
        return cls.CREDIT_COSTS.get(operation, 1)

    @classmethod
    async def report_scan(
        cls,
        user_email: str,
        scan_type: str,
        target: str,
        user_id: str
    ) -> bool:
        """
        Convenience method to report scan usage.

        Args:
            user_email: User's email (used as external_customer_id)
            scan_type: Type of scan (e.g., "red_team", "owasp")
            target: Scan target
            user_id: User who ran the scan

        Returns:
            True if reported successfully
        """
        operation = f"scan_{scan_type}"
        credits = cls.get_operation_cost(operation)

        metadata = {
            "scan_type": scan_type,
            "target": target,
            "user_id": user_id
        }

        return await cls.report_credit_usage(
            external_customer_id=user_email,  # Use email as customer identifier
            credits=credits,
            operation=operation,
            metadata=metadata
        )

    @classmethod
    async def get_customer_usage(cls, external_customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current usage for a customer from Polar.

        Args:
            external_customer_id: Your internal customer ID (email)

        Returns:
            {
                "consumed_units": 150,
                "credited_units": 100,
                "balance": -50  # Negative = overage
            }
        """
        if not cls.POLAR_ACCESS_TOKEN:
            return None

        headers = {
            "Authorization": f"Bearer {cls.POLAR_ACCESS_TOKEN}",
        }

        try:
            response = requests.get(
                f"{cls.POLAR_API_URL}/v1/customer-meters/",
                params={"external_customer_id": external_customer_id},
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    meter = data["items"][0]  # Get first meter
                    return {
                        "consumed_units": meter.get("consumed_units", 0),
                        "credited_units": meter.get("credited_units", 0),
                        "balance": meter.get("balance", 0),
                        "overage": max(0, -meter.get("balance", 0))
                    }

            return None

        except Exception as e:
            logger.error(f"Failed to get customer usage: {str(e)}")
            return None
