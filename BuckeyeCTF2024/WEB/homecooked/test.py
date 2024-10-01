from jinja2 import Environment, Template

# Mocking the 'request' object (you can mock any object as needed)
class MockRequest:
    pass

# Set up Jinja2 environment
env = Environment()

# Template string
template_string = '{{ request | attr(["request."."__","class","__"]) }}'

# Create a Jinja2 template object
template = env.from_string(template_string)

# Create a mock request object
request = MockRequest()

# Render the template with the mock request
output = template.render(request=request)

# Print the result
print(output)

