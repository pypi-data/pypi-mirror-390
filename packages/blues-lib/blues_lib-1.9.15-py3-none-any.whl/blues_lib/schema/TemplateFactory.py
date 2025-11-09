import json
import os
import jsonschema


class TemplateFactory:
    """
    Factory class for loading and managing JSON Schema templates from files
    """
    
    def __init__(self, templates_dir=None):
        """
        Initialize the template factory
        
        Args:
            templates_dir: Directory containing template files. If None, uses the default templates directory.
        """
        # Set default templates directory if not provided
        if templates_dir is None:
            # Get the directory of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.templates_dir = os.path.join(current_dir, 'templates')
        else:
            self.templates_dir = templates_dir
        
        # Cache loaded templates
        self._templates_cache = {}
    
    def get_template(self, template_name):
        """
        Get a template by name
        
        Args:
            template_name: Name of the template (without .json extension)
            
        Returns:
            dict: The template schema
            
        Raises:
            FileNotFoundError: If the template file doesn't exist
            ValueError: If the template is invalid
        """
        # Check cache first
        if template_name in self._templates_cache:
            return self._templates_cache[template_name]
        
        # Construct template file path
        template_file = os.path.join(self.templates_dir, f'{template_name}.json')
        
        # Check if file exists
        if not os.path.exists(template_file):
            raise FileNotFoundError(f'Template file not found: {template_file}')
        
        # Load template from file
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            # Validate the template is a valid JSON Schema
            jsonschema.validators.validator_for(template).check_schema(template)
            
            # Cache the template
            self._templates_cache[template_name] = template
            
            return template
        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON in template file {template_file}: {str(e)}')
        except Exception as e:
            raise ValueError(f'Error loading template {template_file}: {str(e)}')
    
    def list_templates(self):
        """
        List all available templates
        
        Returns:
            list: Names of available templates (without .json extension)
        """
        templates = []
        
        # Check if templates directory exists
        if not os.path.exists(self.templates_dir):
            return templates
        
        # List all .json files in the templates directory
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_name = filename[:-5]  # Remove .json extension
                templates.append(template_name)
        
        return sorted(templates)
    
    def add_template(self, template_name, template):
        """
        Add a template to the cache (in-memory only)
        
        Args:
            template_name: Name of the template
            template: Template schema dictionary
            
        Raises:
            ValueError: If the template is invalid
        """
        # Validate the template is a valid JSON Schema
        try:
            jsonschema.validators.validator_for(template).check_schema(template)
            self._templates_cache[template_name] = template
        except Exception as e:
            raise ValueError(f'Invalid JSON Schema: {str(e)}')
    
    def clear_cache(self):
        """
        Clear the template cache
        """
        self._templates_cache.clear()


# Create a default instance for convenience
default_factory = TemplateFactory()