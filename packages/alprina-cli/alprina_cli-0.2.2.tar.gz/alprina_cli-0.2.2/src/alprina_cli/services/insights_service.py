"""
Insights Service - Provides security analytics and trend analysis
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ..api.services.neon_service import NeonService


class InsightsService:
    """Service for generating security insights and recommendations"""

    def __init__(self):
        self.db = NeonService()

    def get_weekly_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get weekly security summary for a user

        Returns:
            Dictionary with weekly stats including new findings, scan count, etc.
        """
        try:
            # Get critical findings this week
            critical_query = """
                SELECT COUNT(*) as count
                FROM alerts
                WHERE user_id = %s
                AND severity = 'critical'
                AND created_at >= NOW() - INTERVAL '7 days'
            """
            critical_result = self.db.execute_query(critical_query, (user_id,))
            critical_count = critical_result[0]['count'] if critical_result else 0

            # Get high findings this week
            high_query = """
                SELECT COUNT(*) as count
                FROM alerts
                WHERE user_id = %s
                AND severity = 'high'
                AND created_at >= NOW() - INTERVAL '7 days'
            """
            high_result = self.db.execute_query(high_query, (user_id,))
            high_count = high_result[0]['count'] if high_result else 0

            # Get total scans this week
            scans_query = """
                SELECT COUNT(*) as count
                FROM scans
                WHERE user_id = %s
                AND created_at >= NOW() - INTERVAL '7 days'
            """
            scans_result = self.db.execute_query(scans_query, (user_id,))
            scans_count = scans_result[0]['count'] if scans_result else 0

            # Get total vulnerabilities found this week
            vulns_query = """
                SELECT COALESCE(SUM(
                    COALESCE(critical_count, 0) +
                    COALESCE(high_count, 0) +
                    COALESCE(medium_count, 0) +
                    COALESCE(low_count, 0)
                ), 0) as total_vulnerabilities
                FROM scans
                WHERE user_id = %s
                AND created_at >= NOW() - INTERVAL '7 days'
            """
            vulns_result = self.db.execute_query(vulns_query, (user_id,))
            total_vulns = int(vulns_result[0]['total_vulnerabilities']) if vulns_result else 0

            return {
                'critical_findings': critical_count,
                'high_findings': high_count,
                'total_scans': scans_count,
                'total_vulnerabilities': total_vulns,
                'period': 'last_7_days'
            }

        except Exception as e:
            print(f"❌ Error getting weekly summary: {e}")
            return {
                'critical_findings': 0,
                'high_findings': 0,
                'total_scans': 0,
                'total_vulnerabilities': 0,
                'period': 'last_7_days'
            }

    def get_most_scanned_target(self, user_id: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get the most frequently scanned target

        Args:
            user_id: User ID
            days: Number of days to look back (default: 30)

        Returns:
            Dictionary with target and scan count, or None
        """
        try:
            query = """
                SELECT target, COUNT(*) as scan_count
                FROM scans
                WHERE user_id = %s
                AND created_at >= NOW() - INTERVAL '%s days'
                AND target IS NOT NULL
                AND target != ''
                GROUP BY target
                ORDER BY scan_count DESC
                LIMIT 1
            """
            result = self.db.execute_query(query, (user_id, days))

            if result and len(result) > 0:
                return {
                    'target': result[0]['target'],
                    'scan_count': result[0]['scan_count']
                }

            return None

        except Exception as e:
            print(f"❌ Error getting most scanned target: {e}")
            return None

    def get_security_trend(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate security trend (improving or declining)
        Compares current week vs previous week

        Returns:
            Dictionary with trend direction and percentage change
        """
        try:
            # Current week (last 7 days)
            current_query = """
                SELECT
                    COALESCE(SUM(COALESCE(critical_count, 0)), 0) as critical,
                    COALESCE(SUM(COALESCE(high_count, 0)), 0) as high,
                    COALESCE(SUM(COALESCE(medium_count, 0)), 0) as medium
                FROM scans
                WHERE user_id = %s
                AND created_at >= NOW() - INTERVAL '7 days'
            """
            current_result = self.db.execute_query(current_query, (user_id,))

            # Previous week (7-14 days ago)
            previous_query = """
                SELECT
                    COALESCE(SUM(COALESCE(critical_count, 0)), 0) as critical,
                    COALESCE(SUM(COALESCE(high_count, 0)), 0) as high,
                    COALESCE(SUM(COALESCE(medium_count, 0)), 0) as medium
                FROM scans
                WHERE user_id = %s
                AND created_at >= NOW() - INTERVAL '14 days'
                AND created_at < NOW() - INTERVAL '7 days'
            """
            previous_result = self.db.execute_query(previous_query, (user_id,))

            if not current_result or not previous_result:
                return {
                    'trend': 'stable',
                    'direction': 'none',
                    'change_percentage': 0,
                    'message': 'Not enough data for trend analysis'
                }

            # Calculate weighted score (critical=3, high=2, medium=1)
            current_score = (
                int(current_result[0]['critical']) * 3 +
                int(current_result[0]['high']) * 2 +
                int(current_result[0]['medium']) * 1
            )

            previous_score = (
                int(previous_result[0]['critical']) * 3 +
                int(previous_result[0]['high']) * 2 +
                int(previous_result[0]['medium']) * 1
            )

            # Calculate change
            if previous_score == 0:
                if current_score == 0:
                    return {
                        'trend': 'stable',
                        'direction': 'none',
                        'change_percentage': 0,
                        'message': 'No security issues detected'
                    }
                else:
                    return {
                        'trend': 'declining',
                        'direction': 'down',
                        'change_percentage': 100,
                        'message': 'New security issues detected this week'
                    }

            change_percentage = ((current_score - previous_score) / previous_score) * 100

            # Determine trend (negative change = improving, positive = declining)
            if change_percentage < -10:
                trend = 'improving'
                direction = 'up'
                message = f"Security improved by {abs(int(change_percentage))}% this week"
            elif change_percentage > 10:
                trend = 'declining'
                direction = 'down'
                message = f"Security declined by {int(change_percentage)}% this week"
            else:
                trend = 'stable'
                direction = 'none'
                message = "Security posture is stable"

            return {
                'trend': trend,
                'direction': direction,
                'change_percentage': abs(int(change_percentage)),
                'message': message,
                'current_score': current_score,
                'previous_score': previous_score
            }

        except Exception as e:
            print(f"❌ Error calculating security trend: {e}")
            return {
                'trend': 'stable',
                'direction': 'none',
                'change_percentage': 0,
                'message': 'Unable to calculate trend'
            }

    def get_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate smart security recommendations based on scan history

        Returns:
            List of recommendation dictionaries
        """
        try:
            recommendations = []

            # Check for critical findings
            critical_query = """
                SELECT COUNT(*) as count
                FROM alerts
                WHERE user_id = %s
                AND severity = 'critical'
                AND is_read = false
            """
            critical_result = self.db.execute_query(critical_query, (user_id,))
            critical_unread = critical_result[0]['count'] if critical_result else 0

            if critical_unread > 0:
                recommendations.append({
                    'priority': 'critical',
                    'title': 'Urgent: Address Critical Security Issues',
                    'description': f'You have {critical_unread} unread critical security finding{"s" if critical_unread != 1 else ""}. These require immediate attention.',
                    'action': 'View Critical Alerts',
                    'action_url': '/dashboard/alerts?severity=critical'
                })

            # Check scan frequency
            recent_scans_query = """
                SELECT COUNT(*) as count
                FROM scans
                WHERE user_id = %s
                AND created_at >= NOW() - INTERVAL '7 days'
            """
            recent_result = self.db.execute_query(recent_scans_query, (user_id,))
            recent_scans = recent_result[0]['count'] if recent_result else 0

            if recent_scans == 0:
                recommendations.append({
                    'priority': 'medium',
                    'title': 'No Recent Security Scans',
                    'description': 'You haven\'t run any security scans this week. Regular scanning helps identify vulnerabilities early.',
                    'action': 'Run a Scan Now',
                    'action_url': '/dashboard'
                })
            elif recent_scans < 3:
                recommendations.append({
                    'priority': 'low',
                    'title': 'Increase Scan Frequency',
                    'description': 'Consider running security scans more frequently to catch issues early. Aim for at least weekly scans.',
                    'action': 'Schedule Regular Scans',
                    'action_url': '/dashboard/settings'
                })

            # Check for most common vulnerability types
            vuln_types_query = """
                SELECT
                    COALESCE(SUM(COALESCE(critical_count, 0)), 0) as critical,
                    COALESCE(SUM(COALESCE(high_count, 0)), 0) as high,
                    COALESCE(SUM(COALESCE(medium_count, 0)), 0) as medium
                FROM scans
                WHERE user_id = %s
                AND created_at >= NOW() - INTERVAL '30 days'
            """
            vuln_result = self.db.execute_query(vuln_types_query, (user_id,))

            if vuln_result:
                total_vulns = (
                    int(vuln_result[0]['critical']) +
                    int(vuln_result[0]['high']) +
                    int(vuln_result[0]['medium'])
                )

                if total_vulns > 20:
                    recommendations.append({
                        'priority': 'high',
                        'title': 'High Volume of Vulnerabilities',
                        'description': f'Detected {total_vulns} vulnerabilities in the last 30 days. Consider implementing automated security controls.',
                        'action': 'View Scan History',
                        'action_url': '/dashboard/scans'
                    })

            # If no recommendations, add a positive one
            if len(recommendations) == 0:
                recommendations.append({
                    'priority': 'info',
                    'title': 'Security Looking Good!',
                    'description': 'Your security posture is strong. Keep up the regular scanning and monitoring.',
                    'action': 'View Analytics',
                    'action_url': '/dashboard/analytics'
                })

            return recommendations

        except Exception as e:
            print(f"❌ Error generating recommendations: {e}")
            return [{
                'priority': 'info',
                'title': 'Welcome to Alprina',
                'description': 'Start by running your first security scan to get personalized recommendations.',
                'action': 'Get Started',
                'action_url': '/dashboard'
            }]

    def get_top_vulnerable_targets(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get targets with the most vulnerabilities

        Args:
            user_id: User ID
            limit: Number of targets to return

        Returns:
            List of targets with vulnerability counts
        """
        try:
            query = """
                SELECT
                    target,
                    COALESCE(SUM(COALESCE(critical_count, 0)), 0) as critical,
                    COALESCE(SUM(COALESCE(high_count, 0)), 0) as high,
                    COALESCE(SUM(COALESCE(medium_count, 0)), 0) as medium,
                    COALESCE(SUM(COALESCE(low_count, 0)), 0) as low,
                    COUNT(*) as scan_count,
                    MAX(created_at) as last_scan
                FROM scans
                WHERE user_id = %s
                AND created_at >= NOW() - INTERVAL '30 days'
                AND target IS NOT NULL
                AND target != ''
                GROUP BY target
                ORDER BY (
                    COALESCE(SUM(COALESCE(critical_count, 0)), 0) * 3 +
                    COALESCE(SUM(COALESCE(high_count, 0)), 0) * 2 +
                    COALESCE(SUM(COALESCE(medium_count, 0)), 0) * 1
                ) DESC
                LIMIT %s
            """
            results = self.db.execute_query(query, (user_id, limit))

            if not results:
                return []

            targets = []
            for row in results:
                targets.append({
                    'target': row['target'],
                    'critical': int(row['critical']),
                    'high': int(row['high']),
                    'medium': int(row['medium']),
                    'low': int(row['low']),
                    'total_vulnerabilities': int(row['critical']) + int(row['high']) + int(row['medium']) + int(row['low']),
                    'scan_count': int(row['scan_count']),
                    'last_scan': row['last_scan'].isoformat() if row['last_scan'] else None
                })

            return targets

        except Exception as e:
            print(f"❌ Error getting vulnerable targets: {e}")
            return []
