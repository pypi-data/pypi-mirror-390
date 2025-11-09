"""Enhanced validator module with fluent validation rules."""

import re
from typing import Dict, List, Any, Callable
from ..errors.api_errors import ValidationError


class EnhancedValidator:
    """Enhanced validator with fluent validation rules."""
    
    @staticmethod
    def validate_body(body: Dict[str, Any], rules: Dict[str, str]) -> None:
        """
        Validate request body with rules.
        
        Args:
            body: Request body
            rules: Dictionary of field names to rule strings
            
        Raises:
            ValidationError: If validation fails
        """
        errors: Dict[str, List[str]] = {}
        
        for field, rule_string in rules.items():
            value = body.get(field)
            field_errors = EnhancedValidator._validate_field(field, value, rule_string)
            
            if field_errors:
                errors[field] = field_errors
        
        if errors:
            raise ValidationError('Validation failed', field_errors=errors)
    
    @staticmethod
    def _validate_field(field: str, value: Any, rule_string: str) -> List[str]:
        """
        Validate a single field with rules.
        
        Args:
            field: Field name
            value: Field value
            rule_string: Pipe-separated rule string
            
        Returns:
            List of error messages
        """
        errors = []
        rules = rule_string.split('|')
        
        for rule in rules:
            parts = rule.split(':')
            rule_name = parts[0]
            rule_param = parts[1] if len(parts) > 1 else None
            
            if rule_name == 'required':
                if value is None or (isinstance(value, str) and not value):
                    errors.append(f'{field} is required')
            
            elif rule_name == 'string':
                if value is not None and not isinstance(value, str):
                    errors.append(f'{field} must be a string')
            
            elif rule_name in ['number', 'int', 'integer']:
                if value is not None and not isinstance(value, (int, float)):
                    errors.append(f'{field} must be a number')
            
            elif rule_name in ['boolean', 'bool']:
                if value is not None and not isinstance(value, bool):
                    errors.append(f'{field} must be a boolean')
            
            elif rule_name in ['array', 'list']:
                if value is not None and not isinstance(value, list):
                    errors.append(f'{field} must be an array')
            
            elif rule_name in ['map', 'object', 'dict']:
                if value is not None and not isinstance(value, dict):
                    errors.append(f'{field} must be an object')
            
            elif rule_name == 'email':
                if value is not None and isinstance(value, str):
                    email_regex = re.compile(r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$')
                    if not email_regex.match(value):
                        errors.append(f'{field} must be a valid email address')
            
            elif rule_name == 'min':
                if rule_param and value is not None:
                    try:
                        min_value = float(rule_param)
                        if isinstance(value, str) and len(value) < min_value:
                            errors.append(f'{field} must be at least {int(min_value)} characters long')
                        elif isinstance(value, (int, float)) and value < min_value:
                            errors.append(f'{field} must be at least {min_value}')
                        elif isinstance(value, list) and len(value) < min_value:
                            errors.append(f'{field} must contain at least {int(min_value)} items')
                    except ValueError:
                        pass
            
            elif rule_name == 'max':
                if rule_param and value is not None:
                    try:
                        max_value = float(rule_param)
                        if isinstance(value, str) and len(value) > max_value:
                            errors.append(f'{field} must be at most {int(max_value)} characters long')
                        elif isinstance(value, (int, float)) and value > max_value:
                            errors.append(f'{field} must be at most {max_value}')
                        elif isinstance(value, list) and len(value) > max_value:
                            errors.append(f'{field} must contain at most {int(max_value)} items')
                    except ValueError:
                        pass
            
            elif rule_name == 'in':
                if rule_param and value is not None:
                    allowed_values = rule_param.split(',')
                    if str(value) not in allowed_values:
                        errors.append(f'{field} must be one of: {", ".join(allowed_values)}')
            
            elif rule_name in ['regex', 'pattern']:
                if rule_param and value is not None and isinstance(value, str):
                    try:
                        regex = re.compile(rule_param)
                        if not regex.match(value):
                            errors.append(f'{field} format is invalid')
                    except re.error:
                        errors.append(f'Invalid regex pattern for {field}')
            
            elif rule_name == 'url':
                if value is not None and isinstance(value, str):
                    url_regex = re.compile(
                        r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
                    )
                    if not url_regex.match(value):
                        errors.append(f'{field} must be a valid URL')
            
            elif rule_name == 'uuid':
                if value is not None and isinstance(value, str):
                    uuid_regex = re.compile(
                        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                        re.IGNORECASE
                    )
                    if not uuid_regex.match(value):
                        errors.append(f'{field} must be a valid UUID')
        
        return errors
    
    @staticmethod
    def custom_validator(
        field: str,
        validator: Callable[[Any], bool],
        error_message: str
    ) -> Callable[[Any], None]:
        """
        Create a custom validator function.
        
        Args:
            field: Field name
            validator: Validation function
            error_message: Error message if validation fails
            
        Returns:
            Validator function
        """
        def validate(value: Any) -> None:
            if not validator(value):
                raise ValidationError(error_message, field_errors={field: [error_message]})
        return validate
    
    @staticmethod
    def validate_custom(
        body: Dict[str, Any],
        validators: Dict[str, Callable[[Any], bool]]
    ) -> None:
        """
        Validate multiple fields at once with custom validators.
        
        Args:
            body: Request body
            validators: Dictionary of field names to validator functions
            
        Raises:
            ValidationError: If validation fails
        """
        errors: Dict[str, List[str]] = {}
        
        for field, validator in validators.items():
            value = body.get(field)
            if not validator(value):
                errors[field] = [f'{field} validation failed']
        
        if errors:
            raise ValidationError('Validation failed', field_errors=errors)
