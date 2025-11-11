import requests, json, time, threading, os, shutil, tempfile, random, glob, traceback, sys, io
from functools import wraps
from typing import Any, Dict, List, Optional
from template_generator.utils import deviceInfo

class StatsReporter:
    def __init__(self):
        self.primary_domain = "api.dalipen.com"
        self.backup_domain = "aigc.zjtemplate.com"
        self.endpoint = "template_sdk/stat"
        self.timeout = 5
        self.max_sample_size = 10
        
        self._thread_local = threading.local()
        
        if os.name == 'nt':
            self._stats_dir = os.path.join(os.environ.get('TEMP', ''), 'template_generator_stats')
        else:
            self._stats_dir = os.path.join(tempfile.gettempdir(), 'template_generator_stats')
        os.makedirs(self._stats_dir, exist_ok=True)
    
    def _start_log_capture(self):
        """开始日志捕获"""
        try:
            if not hasattr(self._thread_local, 'log_buffer'):
                self._thread_local.log_buffer = io.StringIO()
                self._thread_local.original_stdout = sys.stdout
                self._thread_local.stdout_wrapper = self._create_stdout_wrapper()
                sys.stdout = self._thread_local.stdout_wrapper
        except Exception:
            pass
    
    def _create_stdout_wrapper(self):
        """创建双重输出的stdout包装器"""
        class StdoutWrapper:
            def __init__(self, original_stdout, log_buffer):
                self.original_stdout = original_stdout
                self.log_buffer = log_buffer
            
            def write(self, message):
                try:
                    self.original_stdout.write(message)
                    self.original_stdout.flush()
                except Exception:
                    pass
                try:
                    self.log_buffer.write(message)
                except Exception:
                    pass
            
            def flush(self):
                try:
                    self.original_stdout.flush()
                except Exception:
                    pass
            
            def __getattr__(self, name):
                return getattr(self.original_stdout, name)
        
        return StdoutWrapper(self._thread_local.original_stdout, self._thread_local.log_buffer)
    
    def _stop_log_capture(self):
        try:
            if hasattr(self._thread_local, 'original_stdout'):
                sys.stdout = self._thread_local.original_stdout
                self._thread_local.original_stdout = None
        except Exception:
            pass
    
    def _get_last_logs(self, lines: int = 100) -> str:
        try:
            if hasattr(self._thread_local, 'log_buffer'):
                log_content = self._thread_local.log_buffer.getvalue()
                if log_content:
                    log_lines = log_content.split('\n')
                    last_lines = [line for line in log_lines[-lines:] if line.strip()]
                    return '\n'.join(last_lines)
        except Exception:
            pass
        return ""
    
    def _should_capture_logs(self, error: Exception) -> bool:
        if not error:
            return False
        error_str = str(error).lower()
        return any(keyword in error_str for keyword in [
            'executetemplate err', 'output file not found', 'generatetemplate err'
        ])
    
    def _write_to_file(self, data: Dict[str, Any]):
        try:
            file_index = random.randint(0, 100)
            filename = f"stats_{file_index:02d}.jsonl"
            stats_file = os.path.join(self._stats_dir, filename)
            with open(stats_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
                f.flush()
        except Exception as e:
            pass
    
    def _read_all_files(self):
        try:
            pattern = os.path.join(self._stats_dir, "stats_*.jsonl")
            files = glob.glob(pattern)
            
            all_events = []
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for line in lines:
                                try:
                                    event = json.loads(line.strip())
                                    all_events.append(event)
                                except Exception as e:
                                    continue
                except Exception as e:
                    continue
            
            return all_events
        except Exception as e:
            return []
    
    def _clear_all_files(self):
        try:
            shutil.rmtree(self._stats_dir)
            os.makedirs(self._stats_dir, exist_ok=True)
        except Exception as e:
            pass
    
    def _aggregate_events(self, events: List[Dict[str, Any]]):
        try:
            function_stats = {}
            
            for event in events:
                function_name = event.get('function_name', 'unknown')
                
                if function_name not in function_stats:
                    function_stats[function_name] = {
                        'count': 0,
                        'success_count': 0,
                        'error_count': 0,
                        'samples': []
                    }
                
                stats = function_stats[function_name]
                stats['count'] += 1
                
                if event.get('success', True):
                    stats['success_count'] += 1
                else:
                    stats['error_count'] += 1
                
                if len(stats['samples']) < self.max_sample_size:
                    sample = {
                        'timestamp': event.get('timestamp'),
                        'args': event.get('args', []),
                        'kwargs': event.get('kwargs', {}),
                        'success': event.get('success', True),
                        'error_message': event.get('error_message')
                    }
                    stats['samples'].append(sample)
                elif random.random() < self.max_sample_size / stats['count']:
                    sample = {
                        'timestamp': event.get('timestamp'),
                        'args': event.get('args', []),
                        'kwargs': event.get('kwargs', {}),
                        'success': event.get('success', True),
                        'error_message': event.get('error_message')
                    }
                    stats['samples'][random.randint(0, self.max_sample_size - 1)] = sample
            
            return function_stats
        except Exception as e:
            return {}
    
    def _send_report(self, function_stats: Dict[str, Any]):
        for domain in [self.primary_domain, self.backup_domain]:
            try:
                requests.adapters.DEFAULT_RETRIES = 2
                s = requests.session()
                s.keep_alive = False
                s.headers.update({'Connection':'close'})
                res = s.post(f"https://{domain}/{self.endpoint}",
                                data={
                                "device_info": json.dumps(deviceInfo()),
                                "function_stats": json.dumps(function_stats)
                            }, 
                                verify=False,
                                timeout=self.timeout)
                if res.status_code == 200:
                    return
            except:
                continue
    
    def _get_cache_dir_size(self):
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self._stats_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return total_size
        except Exception:
            return 0
    
    def report_function_call(self, function_name: str, args: tuple, kwargs: dict, result: Any = None, error: Exception = None):
        try:
            error_message = None
            if error:
                error_str = str(error)
                if self._should_capture_logs(error):
                    logs = self._get_last_logs(100)
                    if logs:
                        error_message = f"Logs (last 100 lines):\n{logs}\n\nError: {error_str}"
                    else:
                        error_message = error_str
                else:
                    error_message = error_str
                
                if len(error_message) > 2000:
                    error_message = error_message[:2000] + "\n\n...\n(truncated)"
            
            report_data = {
                "function_name": function_name,
                "timestamp": int(time.time() * 1000),
                "args": self._serialize_args(args),
                "kwargs": self._serialize_kwargs(kwargs),
                "success": error is None,
                "error_message": error_message
            }
            self._write_to_file(report_data)
                
            report_probability = 0.05
            if random.random() < 0.1:
                cache_size = self._get_cache_dir_size()
                if cache_size > 50 * 1024:
                    report_probability = 0.5
            
            if random.random() < report_probability:
                events = self._read_all_files()
                if events:
                    function_stats = self._aggregate_events(events)
                    if function_stats:
                        self._send_report(function_stats)
                        self._clear_all_files()
        except Exception as e:
            print(e)
            pass
    
    def _serialize_args(self, args: tuple) -> List[Any]:
        serialized = []
        for arg in args:
            try:
                if isinstance(arg, (str, int, float, bool, type(None))):
                    serialized.append(arg)
                elif isinstance(arg, (list, dict)):
                    serialized.append(str(arg)[:500])
                else:
                    serialized.append(str(type(arg).__name__))
            except Exception as e:
                serialized.append("unserializable")
        return serialized
    
    def _serialize_kwargs(self, kwargs: dict) -> Dict[str, Any]:
        serialized = {}
        for key, value in kwargs.items():
            try:
                if isinstance(value, (str, int, float, bool, type(None))):
                    serialized[key] = value
                elif isinstance(value, (list, dict)):
                    serialized[key] = str(value)[:500]
                else:
                    serialized[key] = str(type(value).__name__)
            except Exception as e:
                serialized[key] = "unserializable"
        return serialized

_stats_reporter = StatsReporter()

def report_function_stats(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        error = None
        
        _stats_reporter._start_log_capture()
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error = e
            raise
        finally:
            _stats_reporter._stop_log_capture()
            try:
                _stats_reporter.report_function_call(
                    func.__name__,
                    args,
                    kwargs,
                    result,
                    error
                )
            except Exception as e:
                pass
    
    return wrapper
