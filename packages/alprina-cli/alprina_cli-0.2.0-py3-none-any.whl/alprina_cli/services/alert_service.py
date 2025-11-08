"""
Alert Service - Creates and manages security alerts and notifications
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime
import resend
from ..api.services.neon_service import NeonService


class AlertService:
    """Service for creating alerts and sending email notifications"""

    def __init__(self):
        self.db = NeonService()
        self.resend_api_key = os.getenv('RESEND_API_KEY')
        if self.resend_api_key:
            resend.api_key = self.resend_api_key

    def create_alert(
        self,
        user_id: str,
        scan_id: Optional[str],
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a new alert in the database

        Args:
            user_id: UUID of the user
            scan_id: UUID of the related scan (optional)
            alert_type: Type of alert (critical_finding, high_finding, scan_complete, scan_failed, subscription_expiring)
            severity: Severity level (critical, high, medium, low, info)
            title: Alert title
            message: Alert message
            action_url: URL for user to take action (optional)
            metadata: Additional metadata (optional)

        Returns:
            Alert ID if successful, None otherwise
        """
        try:
            query = """
                SELECT create_alert(
                    %s::UUID, %s::UUID, %s, %s, %s, %s, %s, %s::JSONB
                ) as alert_id
            """
            result = self.db.execute_query(
                query,
                (user_id, scan_id, alert_type, severity, title, message, action_url, metadata or {})
            )

            if result and len(result) > 0:
                alert_id = result[0]['alert_id']

                # Check if user wants email notification for this alert type
                should_send_email = self._should_send_email(user_id, alert_type)

                if should_send_email:
                    self._send_email_notification(user_id, alert_id, title, message, action_url)

                return alert_id

            return None

        except Exception as e:
            print(f"❌ Error creating alert: {e}")
            return None

    def _should_send_email(self, user_id: str, alert_type: str) -> bool:
        """Check if user has email notifications enabled for this alert type"""
        try:
            # Map alert_type to preference column
            preference_map = {
                'critical_finding': 'email_critical_findings',
                'high_finding': 'email_high_findings',
                'scan_complete': 'email_scan_complete',
                'scan_failed': 'email_scan_failed',
                'subscription_expiring': 'email_subscription_expiring'
            }

            preference_column = preference_map.get(alert_type)
            if not preference_column:
                return False

            query = f"""
                SELECT {preference_column}
                FROM user_notification_preferences
                WHERE user_id = %s
            """
            result = self.db.execute_query(query, (user_id,))

            if result and len(result) > 0:
                return result[0][preference_column]

            # Default to True if no preferences found
            return True

        except Exception as e:
            print(f"⚠️ Error checking email preferences: {e}")
            return False

    def _send_email_notification(
        self,
        user_id: str,
        alert_id: str,
        title: str,
        message: str,
        action_url: Optional[str]
    ):
        """Send email notification using Resend"""
        if not self.resend_api_key:
            print("⚠️ RESEND_API_KEY not configured, skipping email")
            return

        try:
            # Get user email
            user_query = "SELECT email, full_name FROM users WHERE id = %s"
            user_result = self.db.execute_query(user_query, (user_id,))

            if not user_result or len(user_result) == 0:
                print(f"⚠️ User {user_id} not found")
                return

            user_email = user_result[0]['email']
            user_name = user_result[0].get('full_name') or user_email

            # Build email HTML
            action_button = ""
            if action_url:
                action_button = f"""
                <div style="margin: 30px 0;">
                    <a href="{action_url}"
                       style="background-color: #2563eb; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        View Details
                    </a>
                </div>
                """

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

                <div style="background-color: #f8fafc; border-radius: 8px; padding: 30px; margin-bottom: 20px;">
                    <h1 style="color: #1e293b; margin: 0 0 20px 0; font-size: 24px;">
                        🔔 Security Alert
                    </h1>

                    <p style="margin: 0 0 10px 0; color: #64748b;">
                        Hi {user_name},
                    </p>

                    <div style="background-color: white; border-left: 4px solid #ef4444;
                                padding: 20px; border-radius: 4px; margin: 20px 0;">
                        <h2 style="margin: 0 0 10px 0; font-size: 18px; color: #1e293b;">
                            {title}
                        </h2>
                        <p style="margin: 0; color: #475569;">
                            {message}
                        </p>
                    </div>

                    {action_button}

                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                        <p style="margin: 0; font-size: 14px; color: #64748b;">
                            You're receiving this email because you have email notifications enabled for security alerts.
                            <br>
                            <a href="https://www.alprina.com/dashboard/settings" style="color: #2563eb;">
                                Manage your notification preferences
                            </a>
                        </p>
                    </div>
                </div>

                <div style="text-align: center; color: #94a3b8; font-size: 12px;">
                    <p>
                        Alprina Security Platform<br>
                        <a href="https://www.alprina.com" style="color: #64748b;">www.alprina.com</a>
                    </p>
                </div>
            </body>
            </html>
            """

            # Send email via Resend
            params = {
                "from": "Alprina Security <alerts@alprina.com>",
                "to": [user_email],
                "subject": f"🔔 {title}",
                "html": html_content
            }

            email_response = resend.Emails.send(params)

            # Mark email as sent in database
            update_query = """
                UPDATE alerts
                SET email_sent = true, email_sent_at = NOW()
                WHERE id = %s
            """
            self.db.execute_query(update_query, (alert_id,))

            print(f"✅ Email sent to {user_email} (Alert ID: {alert_id})")

        except Exception as e:
            print(f"❌ Error sending email notification: {e}")

    def mark_alert_read(self, alert_id: str) -> bool:
        """Mark an alert as read"""
        try:
            query = "SELECT mark_alert_read(%s)"
            self.db.execute_query(query, (alert_id,))
            return True
        except Exception as e:
            print(f"❌ Error marking alert as read: {e}")
            return False

    def mark_all_alerts_read(self, user_id: str) -> bool:
        """Mark all user alerts as read"""
        try:
            query = "SELECT mark_all_alerts_read(%s)"
            self.db.execute_query(query, (user_id,))
            return True
        except Exception as e:
            print(f"❌ Error marking all alerts as read: {e}")
            return False

    def get_user_alerts(
        self,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False
    ) -> list:
        """Get alerts for a user"""
        try:
            if unread_only:
                query = """
                    SELECT * FROM alerts
                    WHERE user_id = %s AND is_read = false
                    ORDER BY created_at DESC
                    LIMIT %s
                """
            else:
                query = """
                    SELECT * FROM alerts
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """

            result = self.db.execute_query(query, (user_id, limit))
            return result or []

        except Exception as e:
            print(f"❌ Error getting user alerts: {e}")
            return []

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread alerts for a user"""
        try:
            query = "SELECT get_unread_alert_count(%s) as count"
            result = self.db.execute_query(query, (user_id,))

            if result and len(result) > 0:
                return result[0]['count']

            return 0

        except Exception as e:
            print(f"❌ Error getting unread count: {e}")
            return 0

    def create_scan_completion_alerts(self, scan_id: str, user_id: str, findings: Dict[str, int]):
        """
        Create alerts for scan completion based on findings

        Args:
            scan_id: UUID of the scan
            user_id: UUID of the user
            findings: Dictionary with severity counts (e.g., {'critical': 2, 'high': 5})
        """
        critical_count = findings.get('critical', 0)
        high_count = findings.get('high', 0)

        # Create alert for critical findings
        if critical_count > 0:
            self.create_alert(
                user_id=user_id,
                scan_id=scan_id,
                alert_type='critical_finding',
                severity='critical',
                title=f'🚨 {critical_count} Critical Security {"Issue" if critical_count == 1 else "Issues"} Found',
                message=f'Your recent security scan discovered {critical_count} critical vulnerability{"" if critical_count == 1 else "ies"} that require immediate attention.',
                action_url=f'https://www.alprina.com/dashboard/scans/{scan_id}'
            )

        # Create alert for high severity findings
        if high_count > 0:
            self.create_alert(
                user_id=user_id,
                scan_id=scan_id,
                alert_type='high_finding',
                severity='high',
                title=f'⚠️ {high_count} High Severity {"Issue" if high_count == 1 else "Issues"} Found',
                message=f'Your recent security scan found {high_count} high severity vulnerability{"" if high_count == 1 else "ies"} that should be reviewed soon.',
                action_url=f'https://www.alprina.com/dashboard/scans/{scan_id}'
            )

        # Create general scan complete alert if no critical/high findings
        if critical_count == 0 and high_count == 0:
            total_findings = sum(findings.values())
            if total_findings == 0:
                self.create_alert(
                    user_id=user_id,
                    scan_id=scan_id,
                    alert_type='scan_complete',
                    severity='info',
                    title='✅ Scan Completed Successfully',
                    message='Your security scan completed with no critical or high severity issues found.',
                    action_url=f'https://www.alprina.com/dashboard/scans/{scan_id}'
                )
            else:
                self.create_alert(
                    user_id=user_id,
                    scan_id=scan_id,
                    alert_type='scan_complete',
                    severity='info',
                    title=f'✅ Scan Completed - {total_findings} {"Issue" if total_findings == 1 else "Issues"} Found',
                    message=f'Your security scan completed and found {total_findings} lower severity issue{"" if total_findings == 1 else "s"}.',
                    action_url=f'https://www.alprina.com/dashboard/scans/{scan_id}'
                )
