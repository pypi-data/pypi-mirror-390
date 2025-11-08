from .url_utils import *
def get_parsed_dict(url=None, parsed=None, parsed_dict=None):
    if url and not parsed:
        parsed = parse_url(url)
    if parsed and not parsed_dict:
        parsed_dict = parse_url(parsed=parsed)
    return parsed_dict 
def reconstructUrlFromUrlParse(url=None, parsed=None, parsed_dict=None):
    keys = ['scheme','netloc','path','params','query','fragment']
    parsed_dict =  get_parsed_dict(url=url, parsed=parsed, parsed_dict=parsed_dict)
    if parsed_dict:
        scheme = parsed_dict.get('scheme')
        nuUrl = ''
        for key in keys:
            value = parsed_dict.get(key, '')
            if key == 'scheme':
                nuUrl += f'{value}://' if value else ''
            elif key == 'query':
                nuUrl += f'?{reconstructQuery(value)}' if value else ''
            elif key == 'netloc':
                nuUrl += reconstructNetLoc(value) if value else ''
            else:
                # removed noisy print(value)
                nuUrl += value
        return nuUrl
    return url
def get_youtube_parsed_dict(url=None, parsed=None, parsed_dict=None):
    parsed_dict =  get_parsed_dict(url=url, parsed=parsed, parsed_dict=parsed_dict)
    if parsed_dict:
        netloc = parsed_dict.get("netloc")
        domain = (netloc or {}).get('domain') or ''
        query  = parsed_dict.get('query') or {}
        path   = parsed_dict.get('path') or ''
        if domain.startswith('youtu'):
            # force youtube.com and /watch?v=ID
            netloc['www'] = True
            netloc['domain'] = 'youtube'
            netloc['extention'] = '.com'
            parsed_dict['netloc'] = netloc

            # keep v if present; otherwise derive
            v_query = query.get('v')
            if not v_query:
                if path.startswith('/watch/') or path.startswith('/shorts/'):
                    v_query = eatAll(path, ['/','watch','shorts'])
                else:
                    v_query = eatAll(path, ['/'])
            parsed_dict['path'] = '/watch'
            parsed_dict['query'] = {'v': v_query} if v_query else {}
            return parsed_dict
def get_youtube_v_query(url=None, parsed=None, parsed_dict=None):
    parsed_dict =  get_youtube_parsed_dict(url=url, parsed=parsed, parsed_dict=parsed_dict)
    v_query = parsed_dict.get('query',{}).get('v')
    return v_query
def get_youtube_url(url=None, parsed=None, parsed_dict=None):
    parsed_dict =  get_youtube_parsed_dict(url=url, parsed=parsed, parsed_dict=parsed_dict)
    return reconstructUrlFromUrlParse(parsed_dict=parsed_dict)
def get_threads_url(url=None,parsed=None, parsed_dict =None ):
    parsed_dict =  get_parsed_dict(url=url, parsed=parsed, parsed_dict=parsed_dict)
    if parsed_dict:
        netloc = parsed_dict.get("netloc")
        domain = (netloc or {}).get('domain') or ''
        if domain.startswith('threads'):
            netloc['www']=True
            netloc['domain'] ='threads'
            netloc['extention'] = '.net'
            parsed['netloc']=netloc
            return reconstructUrlFromUrlParse(url=url,parsed=parsed,parsed_dict=None)  
def get_corrected_url(url=None,parsed=None, parsed_dict =None ):
    parsed_dict =  get_parsed_dict(url=url, parsed=parsed, parsed_dict=parsed_dict)
    if parsed_dict:
        funcs = [get_threads_url,get_youtube_url,reconstructUrlFromUrlParse]
        for func in funcs:
            corrected_url = func(url=url,parsed=parsed,parsed_dict=parsed_dict)
            if corrected_url:
                return corrected_url

