from flask import session


def admin_required(f):
    def wrapper(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return "<h2>Access denied. Admins only.</h2>", 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def artist_required(f):
    def wrapper(*args, **kwargs):
        if 'role' not in session or session['role'] != 'artist':
            return "<h2>Access denied. Artists only.</h2>", 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def listener_required(f):
    def wrapper(*args, **kwargs):
        if 'role' not in session or session['role'] != 'listener':
            return "<h2>Access denied. Listeners only.</h2>", 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper