"""
KardoCSS - Components Utilities
Componentes predefinidos para las plantillas
"""

def generate_components():
    """Genera clases CSS para componentes comunes"""
    
    css = """
/* ===================================
   KardoCSS - Components
   =================================== */

/* Cards */
.card {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.card-header {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    font-weight: 600;
}

.card-body {
    padding: 1.5rem;
}

.card-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid #e5e7eb;
    background-color: #f9fafb;
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    line-height: 1.5;
    border-radius: 0.375rem;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-primary {
    background-color: #3b82f6;
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background-color: #2563eb;
}

.btn-secondary {
    background-color: #6b7280;
    color: white;
}

.btn-secondary:hover:not(:disabled) {
    background-color: #4b5563;
}

.btn-success {
    background-color: #10b981;
    color: white;
}

.btn-success:hover:not(:disabled) {
    background-color: #059669;
}

.btn-danger {
    background-color: #ef4444;
    color: white;
}

.btn-danger:hover:not(:disabled) {
    background-color: #dc2626;
}

.btn-warning {
    background-color: #f59e0b;
    color: white;
}

.btn-warning:hover:not(:disabled) {
    background-color: #d97706;
}

.btn-outline {
    background-color: transparent;
    border-color: currentColor;
}

.btn-outline:hover:not(:disabled) {
    background-color: currentColor;
    color: white;
}

.btn-white {
    background-color: white;
    color: #1f2937;
    border-color: #d1d5db;
}

.btn-white:hover:not(:disabled) {
    background-color: #f3f4f6;
}

.btn-sm {
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
}

.btn-lg {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
}

.btn-xl {
    padding: 1rem 2rem;
    font-size: 1.125rem;
}

.btn-link {
    background-color: transparent;
    color: #3b82f6;
    padding: 0;
    border: none;
}

.btn-link:hover:not(:disabled) {
    color: #2563eb;
    text-decoration: underline;
}

/* Navbar */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0;
}

.navbar-brand {
    font-size: 1.5rem;
    font-weight: 700;
    color: inherit;
    text-decoration: none;
}

.navbar-nav {
    display: flex;
    list-style: none;
    gap: 2rem;
    margin: 0;
    padding: 0;
}

.navbar-nav li {
    margin: 0;
}

.nav-link {
    color: inherit;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
}

.nav-link:hover {
    opacity: 0.8;
}

.nav-link.active {
    color: #3b82f6;
}

/* Hero Section */
.hero-section {
    padding: 4rem 0;
    text-align: center;
}

.hero-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.hero-subtitle {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.hero-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

/* Feature Cards */
.feature-card {
    text-align: center;
    padding: 2rem;
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
}

.feature-icon {
    width: 4rem;
    height: 4rem;
    margin: 0 auto 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    border-radius: 50%;
}

/* Stat Cards */
.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Sidebar */
.sidebar {
    width: 16rem;
    background-color: #1f2937;
    color: white;
    height: 100vh;
    position: fixed;
    left: 0;
    top: 0;
    overflow-y: auto;
    transition: transform 0.3s ease;
}

.sidebar.collapsed {
    transform: translateX(-100%);
}

.sidebar-header {
    padding: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-nav {
    padding: 1rem;
}

.sidebar-nav ul {
    list-style: none;
    margin: 0;
    padding: 0;
}

.sidebar-nav li {
    margin-bottom: 0.5rem;
}

.sidebar-nav a {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
    border-radius: 0.375rem;
    transition: all 0.2s ease;
}

.sidebar-nav a:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
}

.sidebar-nav a.active {
    background-color: #3b82f6;
    color: white;
}

/* Tables */
.table {
    width: 100%;
    border-collapse: collapse;
}

.table thead {
    background-color: #f9fafb;
    border-bottom: 2px solid #e5e7eb;
}

.table th {
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    color: #374151;
}

.table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #e5e7eb;
}

.table tbody tr:hover {
    background-color: #f9fafb;
}

/* Alerts */
.alert {
    padding: 1rem 1.5rem;
    border-radius: 0.375rem;
    margin-bottom: 1rem;
}

.alert-info {
    background-color: #dbeafe;
    color: #1e40af;
    border-left: 4px solid #3b82f6;
}

.alert-success {
    background-color: #d1fae5;
    color: #065f46;
    border-left: 4px solid #10b981;
}

.alert-warning {
    background-color: #fef3c7;
    color: #92400e;
    border-left: 4px solid #f59e0b;
}

.alert-danger {
    background-color: #fee2e2;
    color: #991b1b;
    border-left: 4px solid #ef4444;
}

/* Modal */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.modal-content {
    background-color: white;
    border-radius: 0.5rem;
    max-width: 32rem;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-body {
    padding: 1.5rem;
}

.modal-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid #e5e7eb;
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
}

/* Breadcrumb */
.breadcrumb {
    display: flex;
    list-style: none;
    padding: 0;
    margin: 0;
}

.breadcrumb li {
    display: flex;
    align-items: center;
}

.breadcrumb li:not(:last-child)::after {
    content: "/";
    margin: 0 0.5rem;
    color: #6b7280;
}

.breadcrumb a {
    color: #3b82f6;
    text-decoration: none;
}

.breadcrumb a:hover {
    text-decoration: underline;
}

/* Pagination */
.pagination {
    display: flex;
    list-style: none;
    gap: 0.25rem;
    padding: 0;
    margin: 0;
}

.pagination li a {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 2.5rem;
    height: 2.5rem;
    padding: 0 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    color: #374151;
    text-decoration: none;
    transition: all 0.2s ease;
}

.pagination li a:hover {
    background-color: #f3f4f6;
}

.pagination li.active a {
    background-color: #3b82f6;
    color: white;
    border-color: #3b82f6;
}

/* Dropdown */
.dropdown {
    position: relative;
    display: inline-block;
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.375rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    min-width: 10rem;
    margin-top: 0.25rem;
    z-index: 1000;
}

.dropdown-item {
    display: block;
    padding: 0.5rem 1rem;
    color: #374151;
    text-decoration: none;
    transition: background-color 0.2s ease;
}

.dropdown-item:hover {
    background-color: #f3f4f6;
}

/* Tabs */
.tabs {
    display: flex;
    border-bottom: 2px solid #e5e7eb;
    gap: 1rem;
}

.tab {
    padding: 0.75rem 1rem;
    color: #6b7280;
    text-decoration: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s ease;
}

.tab:hover {
    color: #374151;
}

.tab.active {
    color: #3b82f6;
    border-bottom-color: #3b82f6;
}

/* Progress Bar */
.progress {
    height: 1rem;
    background-color: #e5e7eb;
    border-radius: 0.5rem;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background-color: #3b82f6;
    transition: width 0.3s ease;
}

/* Spinner */
.spinner {
    display: inline-block;
    width: 2rem;
    height: 2rem;
    border: 3px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.spinner-sm {
    width: 1rem;
    height: 1rem;
    border-width: 2px;
}

.spinner-lg {
    width: 3rem;
    height: 3rem;
    border-width: 4px;
}

/* Responsive utilities */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem;
    }
    
    .navbar-nav {
        flex-direction: column;
        gap: 1rem;
    }
    
    .hero-actions {
        flex-direction: column;
    }
    
    .sidebar {
        transform: translateX(-100%);
    }
    
    .sidebar.open {
        transform: translateX(0);
    }
}
"""
    
    return css

