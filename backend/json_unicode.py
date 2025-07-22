"""
Custom JSON encoder to ensure proper Unicode handling
"""
import json
from flask import Response

class UnicodeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that ensures Unicode characters are not escaped"""
    def encode(self, o):
        # Get the default encoding
        result = super().encode(o)
        # If it contains escaped unicode, decode it
        if '\\u' in result:
            result = result.encode('utf-8').decode('unicode_escape')
        return result

def jsonify_unicode(data, status=200):
    """Create a JSON response with proper Unicode support"""
    json_str = json.dumps(data, ensure_ascii=False, cls=UnicodeJSONEncoder)
    response = Response(
        json_str,
        status=status,
        mimetype='application/json; charset=utf-8'
    )
    return response
