import jsonschema
from .TemplateFactory import default_factory


class SchemaChecker:
    """
    Class for checking metadata against JSON Schema templates
    """
    
    def __init__(self, template_factory=None):
        """
        Initialize SchemaChecker with a template factory
        
        Args:
            template_factory: TemplateFactory instance to use. If None, uses the default factory.
        """
        # Use provided factory or default factory
        self.template_factory = template_factory if template_factory else default_factory
        
        # In-memory templates that can be added dynamically
        self._dynamic_templates = {}
    
    def check(self, meta, template_name):
        """
        Check if metadata conforms to the specified template
        
        Args:
            meta: Metadata to check
            template_name: Template name
            
        Returns:
            tuple: (is_valid, error_message) where error_message is None if valid
        """
        # First check dynamic templates
        if template_name in self._dynamic_templates:
            schema = self._dynamic_templates[template_name]
        else:
            # Then try to get from template factory
            try:
                schema = self.template_factory.get_template(template_name)
            except FileNotFoundError:
                return False, f'Template {template_name} does not exist'
            except ValueError as e:
                return False, str(e)
        
        # Validate metadata
        try:
            jsonschema.validate(instance=meta, schema=schema)
            return True, None
        except jsonschema.exceptions.ValidationError as e:
            error_message = self._format_error_message(e)
            return False, error_message
        except Exception as e:
            return False, str(e)
    
    def _format_error_message(self, validation_error):
        """
        Format validation error message
        
        Args:
            validation_error: jsonschema ValidationError object
            
        Returns:
            str: Formatted error message
        """
        # Get error path
        path = '/'.join(map(str, validation_error.path))
        if path:
            path = f"at '{path}': "
        
        # Return formatted error message
        return f"{path}{validation_error.message}"
    
    def add_template(self, template_name, schema):
        """
        Add a new template to dynamic templates
        
        Args:
            template_name: Template name
            schema: JSON Schema dictionary
            
        Returns:
            bool: True if added successfully
            
        Raises:
            ValueError: If schema is not a valid JSON Schema
        """
        # Validate schema is a valid JSON Schema
        if self.validate_schema(schema):
            self._dynamic_templates[template_name] = schema
            return True
        raise ValueError("Invalid JSON Schema")
    
    def validate_schema(self, schema):
        """
        Validate if a schema is a valid JSON Schema
        
        Args:
            schema: Schema to validate
            
        Returns:
            bool: True if valid
        """
        try:
            jsonschema.validators.validator_for(schema).check_schema(schema)
            return True
        except Exception:
            return False
    
    def get_templates(self):
        """
        Get all available template names
        
        Returns:
            list: List of template names
        """
        # Combine dynamic templates and factory templates
        factory_templates = self.template_factory.list_templates()
        all_templates = list(set(factory_templates + list(self._dynamic_templates.keys())))
        return sorted(all_templates)