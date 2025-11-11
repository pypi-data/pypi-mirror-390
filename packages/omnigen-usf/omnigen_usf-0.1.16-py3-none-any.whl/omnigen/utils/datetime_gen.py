"""DateTime generation utilities with timezone support."""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pytz


class DateTimeGenerator:
    """
    Generate dynamic datetime values with timezone support.
    
    Supports three modes:
    - single: Use a fixed datetime
    - random_from_range: Random datetime within a range
    - random_from_list: Random selection from a list
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize datetime generator.
        
        Args:
            config: DateTime configuration
        """
        self.config = config
        self.enabled = config.get('enabled', False)
        self.timezone_str = config.get('timezone', 'UTC')
        
        # Initialize timezone
        try:
            self.timezone = pytz.timezone(self.timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            self.timezone = pytz.UTC
            self.timezone_str = 'UTC'
        
        self.mode = config.get('mode', 'single')
        self.output_format = config.get('format', '%Y-%m-%d %H:%M:%S')
    
    def generate(self) -> str:
        """
        Generate datetime string based on configuration.
        
        Returns:
            Formatted datetime string
        """
        if not self.enabled:
            return ''
        
        if self.mode == 'single':
            dt = self._generate_single()
        elif self.mode == 'random_from_range':
            dt = self._generate_from_range()
        elif self.mode == 'random_from_list':
            dt = self._generate_from_list()
        else:
            dt = datetime.now(self.timezone)
        
        # Ensure timezone info
        if dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)
        
        return dt.strftime(self.output_format)
    
    def _generate_single(self) -> datetime:
        """Generate datetime from single configured value."""
        dt_string = self.config.get('single_datetime', '')
        if not dt_string:
            return datetime.now(self.timezone)
        return self._parse_datetime(dt_string)
    
    def _generate_from_range(self) -> datetime:
        """Generate random datetime from range."""
        range_config = self.config.get('range', {})
        start_str = range_config.get('start')
        end_str = range_config.get('end')
        
        if not start_str or not end_str:
            return datetime.now(self.timezone)
        
        start_dt = self._parse_datetime(start_str)
        end_dt = self._parse_datetime(end_str)
        
        if start_dt >= end_dt:
            return start_dt
        
        time_diff = (end_dt - start_dt).total_seconds()
        random_seconds = random.uniform(0, time_diff)
        
        return start_dt + timedelta(seconds=random_seconds)
    
    def _generate_from_list(self) -> datetime:
        """Generate datetime by random selection from list."""
        dt_list = self.config.get('datetime_list', [])
        if not dt_list:
            return datetime.now(self.timezone)
        
        dt_string = random.choice(dt_list)
        return self._parse_datetime(dt_string)
    
    def _parse_datetime(self, dt_string: str) -> datetime:
        """
        Parse datetime string with multiple format attempts.
        
        Args:
            dt_string: Datetime string to parse
            
        Returns:
            Parsed datetime object
        """
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
            '%d-%m-%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                parsed_dt = datetime.strptime(dt_string, fmt)
                if parsed_dt.tzinfo is None:
                    parsed_dt = self.timezone.localize(parsed_dt)
                return parsed_dt
            except ValueError:
                continue
        
        # If all formats fail, return current time
        return datetime.now(self.timezone)