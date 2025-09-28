"""
System Health Monitoring Module
Provides real-time system health metrics and monitoring capabilities
"""

import psutil
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .schemas import SystemHealth
from .audit_logger import AuditLogger
from .json_utils import safe_json_dump

class SystemMonitor:
    """System health monitoring and metrics collection"""
    
    def __init__(self):
        self.start_time = time.time()
        self.audit_logger = AuditLogger()
        self.metrics_file = Path("app/data/system_metrics.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
    def get_system_health(self) -> SystemHealth:
        """Get current system health status"""
        try:
            # Basic system metrics
            uptime = time.time() - self.start_time
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Application-specific metrics
            active_users = self._get_active_users()
            total_validations = self._get_total_validations()
            last_validation = self._get_last_validation()
            error_rate = self._calculate_error_rate()
            avg_response_time = self._get_average_response_time()
            
            # Determine overall status
            status = self._determine_health_status(
                memory.percent, cpu_percent, error_rate
            )
            
            return SystemHealth(
                status=status,
                uptime_seconds=uptime,
                memory_usage_mb=memory.used / (1024 * 1024),
                cpu_usage_percent=cpu_percent,
                active_users=active_users,
                total_validations=total_validations,
                last_validation=last_validation,
                error_rate=error_rate,
                response_time_avg_ms=avg_response_time
            )
            
        except Exception as e:
            # Return critical status if monitoring fails
            return SystemHealth(
                status="CRITICAL",
                uptime_seconds=time.time() - self.start_time,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                active_users=0,
                total_validations=0,
                error_rate=100.0,
                response_time_avg_ms=0
            )
    
    def _get_active_users(self) -> int:
        """Get count of active users (simplified implementation)"""
        try:
            # This could be enhanced with session tracking
            return len(psutil.users()) if hasattr(psutil, 'users') else 1
        except:
            return 1
    
    def _get_total_validations(self) -> int:
        """Get total number of validations performed"""
        try:
            validated_file = Path("app/data/reports/validated.jsonl")
            if validated_file.exists():
                with open(validated_file, 'r') as f:
                    return sum(1 for line in f if line.strip())
            return 0
        except:
            return 0
    
    def _get_last_validation(self) -> Optional[datetime]:
        """Get timestamp of last validation"""
        try:
            validated_file = Path("app/data/reports/validated.jsonl")
            if validated_file.exists():
                with open(validated_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = json.loads(lines[-1])
                        return datetime.fromisoformat(last_line.get('timestamp', ''))
            return None
        except:
            return None
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate from audit logs"""
        try:
            logs = self.audit_logger.get_logs(limit=100)  # Last 100 actions
            if not logs:
                return 0.0
            
            error_count = sum(1 for log in logs if 'error' in log.get('action', '').lower())
            return (error_count / len(logs)) * 100
        except:
            return 0.0
    
    def _get_average_response_time(self) -> float:
        """Get average response time (simplified)"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)
                    response_times = metrics.get('response_times', [])
                    if response_times:
                        return sum(response_times) / len(response_times)
            return 0.0
        except:
            return 0.0
    
    def _determine_health_status(self, memory_percent: float, cpu_percent: float, error_rate: float) -> str:
        """Determine overall system health status"""
        if memory_percent > 90 or cpu_percent > 90 or error_rate > 50:
            return "CRITICAL"
        elif memory_percent > 75 or cpu_percent > 75 or error_rate > 25:
            return "WARNING"
        else:
            return "HEALTHY"
    
    def record_metrics(self, operation: str, duration_ms: float, success: bool = True):
        """Record operation metrics""" 
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'duration_ms': duration_ms,
                'success': success
            }
            
            # Load existing metrics
            existing_metrics = {}
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    existing_metrics = json.load(f)
            
            # Add new metrics
            if 'operations' not in existing_metrics:
                existing_metrics['operations'] = []
            
            existing_metrics['operations'].append(metrics)
            
            # Keep only last 1000 operations
            if len(existing_metrics['operations']) > 1000:
                existing_metrics['operations'] = existing_metrics['operations'][-1000:]
            
            # Update response times
            if 'response_times' not in existing_metrics:
                existing_metrics['response_times'] = []
            existing_metrics['response_times'].append(duration_ms)
            
            # Keep only last 100 response times
            if len(existing_metrics['response_times']) > 100:
                existing_metrics['response_times'] = existing_metrics['response_times'][-100:]
            
            # Save metrics
            with open(self.metrics_file, 'w') as f:
                safe_json_dump(existing_metrics, f, indent=2)
                
        except Exception as e:
            # Fail silently for metrics recording
            pass
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary for dashboard"""
        try:
            health = self.get_system_health()
            
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)
                    
                operations = metrics.get('operations', [])
                response_times = metrics.get('response_times', [])
                
                # Calculate success rate
                successful_ops = sum(1 for op in operations if op.get('success', True))
                success_rate = (successful_ops / len(operations)) * 100 if operations else 100
                
                # Calculate average response time
                avg_response = sum(response_times) / len(response_times) if response_times else 0
                
                return {
                    'system_status': health.status,
                    'uptime_hours': health.uptime_seconds / 3600,
                    'memory_usage_percent': (health.memory_usage_mb / (1024 * 1024)) * 100,
                    'cpu_usage_percent': health.cpu_usage_percent,
                    'total_operations': len(operations),
                    'success_rate': success_rate,
                    'avg_response_time_ms': avg_response,
                    'total_validations': health.total_validations,
                    'error_rate': health.error_rate
                }
            else:
                return {
                    'system_status': health.status,
                    'uptime_hours': health.uptime_seconds / 3600,
                    'memory_usage_percent': 0,
                    'cpu_usage_percent': health.cpu_usage_percent,
                    'total_operations': 0,
                    'success_rate': 100,
                    'avg_response_time_ms': 0,
                    'total_validations': health.total_validations,
                    'error_rate': health.error_rate
                }
                
        except Exception as e:
            return {
                'system_status': 'UNKNOWN',
                'uptime_hours': 0,
                'memory_usage_percent': 0,
                'cpu_usage_percent': 0,
                'total_operations': 0,
                'success_rate': 0,
                'avg_response_time_ms': 0,
                'total_validations': 0,
                'error_rate': 100
            }
    
    def cleanup_old_metrics(self, days: int = 7):
        """Clean up metrics older than specified days"""
        try:
            if not self.metrics_file.exists():
                return
                
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with open(self.metrics_file, 'r') as f:
                metrics = json.load(f)
            
            # Filter operations
            if 'operations' in metrics:
                metrics['operations'] = [
                    op for op in metrics['operations']
                    if datetime.fromisoformat(op['timestamp']) > cutoff_date
                ]
            
            # Save cleaned metrics
            with open(self.metrics_file, 'w') as f:
                safe_json_dump(metrics, f, indent=2)
                
        except Exception as e:
            # Fail silently for cleanup
            pass

# Global system monitor instance
system_monitor = SystemMonitor()
