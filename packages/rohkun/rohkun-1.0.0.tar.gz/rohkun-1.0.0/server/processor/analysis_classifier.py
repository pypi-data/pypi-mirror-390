"""
Analysis Classifier - Detects frameworks and technologies from analysis results.

This module analyzes endpoints and API calls to determine which frameworks
and technologies are being used in the codebase.
"""

import logging
from typing import List, Dict, Any
from collections import Counter

logger = logging.getLogger(__name__)


def detect_framework(endpoints: List[Dict[str, Any]], api_calls: List[Dict[str, Any]]) -> str:
    """
    Detect the primary framework from endpoints and API calls.
    
    Args:
        endpoints: List of detected endpoints
        api_calls: List of detected API calls
        
    Returns:
        Framework name (e.g., "Flask + React", "FastAPI", "Express")
    """
    backend_frameworks = set()
    frontend_frameworks = set()
    
    # Analyze endpoints for backend frameworks
    for endpoint in endpoints:
        detection_method = endpoint.get('detection_method', '').lower()
        file_path = endpoint.get('file_path', '').lower()
        
        # Backend framework detection
        if 'flask' in detection_method or 'flask' in file_path:
            backend_frameworks.add('Flask')
        elif 'fastapi' in detection_method or 'fastapi' in file_path:
            backend_frameworks.add('FastAPI')
        elif 'django' in detection_method or 'django' in file_path:
            backend_frameworks.add('Django')
        elif 'express' in detection_method or 'express' in file_path:
            backend_frameworks.add('Express')
        elif 'spring' in detection_method or 'spring' in file_path:
            backend_frameworks.add('Spring Boot')
        elif 'aspnet' in detection_method or 'asp.net' in file_path or '.net' in file_path:
            backend_frameworks.add('ASP.NET')
        elif 'go' in detection_method and ('handler' in detection_method or 'router' in file_path):
            backend_frameworks.add('Go')
        elif 'ruby' in detection_method or 'rails' in file_path:
            backend_frameworks.add('Ruby on Rails')
        elif 'php' in detection_method or 'laravel' in file_path:
            backend_frameworks.add('PHP/Laravel')
        elif 'serverless' in detection_method or 'lambda' in file_path:
            backend_frameworks.add('Serverless')
    
    # Analyze API calls for frontend frameworks
    for api_call in api_calls:
        file_path = api_call.get('file_path', '').lower()
        detection_method = api_call.get('detection_method', '').lower()
        
        # Frontend framework detection
        if any(ext in file_path for ext in ['.jsx', '.tsx']) or 'react' in file_path:
            frontend_frameworks.add('React')
        elif 'vue' in file_path or '.vue' in file_path:
            frontend_frameworks.add('Vue')
        elif 'angular' in file_path or 'ng' in detection_method:
            frontend_frameworks.add('Angular')
        elif 'svelte' in file_path:
            frontend_frameworks.add('Svelte')
        elif 'next' in file_path or 'nextjs' in detection_method:
            frontend_frameworks.add('Next.js')
        elif 'nuxt' in file_path:
            frontend_frameworks.add('Nuxt.js')
    
    # Combine frameworks
    frameworks = []
    if backend_frameworks:
        # Use most common or first detected
        frameworks.append(sorted(backend_frameworks)[0])
    if frontend_frameworks:
        frameworks.append(sorted(frontend_frameworks)[0])
    
    if frameworks:
        return ' + '.join(frameworks)
    
    # Fallback: try to detect from file extensions
    if endpoints:
        file_paths = [ep.get('file_path', '') for ep in endpoints]
        if any('.py' in fp for fp in file_paths):
            return 'Python'
        elif any('.js' in fp or '.ts' in fp for fp in file_paths):
            return 'Node.js'
        elif any('.java' in fp for fp in file_paths):
            return 'Java'
        elif any('.cs' in fp for fp in file_paths):
            return '.NET'
        elif any('.go' in fp for fp in file_paths):
            return 'Go'
        elif any('.rb' in fp for fp in file_paths):
            return 'Ruby'
        elif any('.php' in fp for fp in file_paths):
            return 'PHP'
    
    return 'Unknown'


def detect_technologies(endpoints: List[Dict[str, Any]], api_calls: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Detect all technologies used in the codebase.
    
    Args:
        endpoints: List of detected endpoints
        api_calls: List of detected API calls
        
    Returns:
        Dictionary with categories of technologies detected
    """
    technologies = {
        'backend': set(),
        'frontend': set(),
        'database': set(),
        'api_protocols': set(),
        'http_clients': set()
    }
    
    # Analyze endpoints
    for endpoint in endpoints:
        detection_method = endpoint.get('detection_method', '').lower()
        file_path = endpoint.get('file_path', '').lower()
        
        # Backend frameworks
        if 'flask' in detection_method:
            technologies['backend'].add('Flask')
        if 'fastapi' in detection_method:
            technologies['backend'].add('FastAPI')
        if 'django' in detection_method:
            technologies['backend'].add('Django')
        if 'express' in detection_method:
            technologies['backend'].add('Express.js')
        if 'spring' in detection_method:
            technologies['backend'].add('Spring Boot')
        
        # API protocols
        if 'graphql' in detection_method or 'graphql' in file_path:
            technologies['api_protocols'].add('GraphQL')
        if 'trpc' in detection_method or 'trpc' in file_path:
            technologies['api_protocols'].add('tRPC')
        if 'grpc' in detection_method or 'grpc' in file_path:
            technologies['api_protocols'].add('gRPC')
        if 'websocket' in detection_method or 'ws' in file_path:
            technologies['api_protocols'].add('WebSocket')
    
    # Analyze API calls
    for api_call in api_calls:
        detection_method = api_call.get('detection_method', '').lower()
        file_path = api_call.get('file_path', '').lower()
        
        # Frontend frameworks
        if 'react' in file_path or '.jsx' in file_path or '.tsx' in file_path:
            technologies['frontend'].add('React')
        if 'vue' in file_path:
            technologies['frontend'].add('Vue.js')
        if 'angular' in file_path:
            technologies['frontend'].add('Angular')
        
        # HTTP clients
        if 'axios' in detection_method:
            technologies['http_clients'].add('Axios')
        if 'fetch' in detection_method:
            technologies['http_clients'].add('Fetch API')
        if 'react_query' in detection_method:
            technologies['http_clients'].add('React Query')
        if 'swr' in detection_method:
            technologies['http_clients'].add('SWR')
        if 'rtk_query' in detection_method:
            technologies['http_clients'].add('RTK Query')
    
    # Convert sets to sorted lists
    return {
        category: sorted(list(techs))
        for category, techs in technologies.items()
        if techs
    }
