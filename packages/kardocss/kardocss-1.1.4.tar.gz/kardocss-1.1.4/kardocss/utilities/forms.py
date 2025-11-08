"""
Generador de utilidades para formularios modernos en KardoCSS
"""

def generate_form_utilities():
    """Genera utilidades CSS para formularios modernos"""
    css = []
    
    # Input y textarea base
    css.append("""
/* ==========================================================================
   FORM UTILITIES
   ========================================================================== */

/* Input base moderno */
.k-input {
    display: block;
    width: 100%;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #374151;
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    transition: all 0.2s ease;
}

.k-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.k-input:disabled {
    background-color: #f3f4f6;
    cursor: not-allowed;
    opacity: 0.6;
}

.k-input::placeholder {
    color: #9ca3af;
}

/* Textarea moderno */
.k-textarea {
    display: block;
    width: 100%;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #374151;
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    transition: all 0.2s ease;
    resize: vertical;
    min-height: 100px;
}

.k-textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Select moderno */
.k-select {
    display: block;
    width: 100%;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #374151;
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    transition: all 0.2s ease;
    cursor: pointer;
}

.k-select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Label moderno */
.k-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
}

/* Form group */
.k-form-group {
    margin-bottom: 1.5rem;
}

/* Input con icono */
.k-input-group {
    position: relative;
    display: flex;
    align-items: center;
}

.k-input-icon {
    position: absolute;
    left: 1rem;
    color: #9ca3af;
    pointer-events: none;
}

.k-input-with-icon {
    padding-left: 2.75rem;
}

/* Tamaños de input */
.k-input-sm {
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
}

.k-input-lg {
    padding: 1rem 1.25rem;
    font-size: 1.125rem;
}

/* Input con error */
.k-input-error {
    border-color: #ef4444;
}

.k-input-error:focus {
    border-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Input con éxito */
.k-input-success {
    border-color: #10b981;
}

.k-input-success:focus {
    border-color: #10b981;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

/* Mensaje de error */
.k-error-message {
    display: block;
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #ef4444;
}

/* Mensaje de ayuda */
.k-help-text {
    display: block;
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
}

/* Checkbox y radio modernos */
.k-checkbox,
.k-radio {
    width: 1.25rem;
    height: 1.25rem;
    border: 2px solid #d1d5db;
    border-radius: 0.25rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.k-radio {
    border-radius: 50%;
}

.k-checkbox:checked,
.k-radio:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

.k-checkbox:focus,
.k-radio:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Switch toggle */
.k-switch {
    position: relative;
    display: inline-block;
    width: 3rem;
    height: 1.75rem;
}

.k-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.k-switch-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #d1d5db;
    transition: 0.3s;
    border-radius: 1.75rem;
}

.k-switch-slider:before {
    position: absolute;
    content: "";
    height: 1.25rem;
    width: 1.25rem;
    left: 0.25rem;
    bottom: 0.25rem;
    background-color: white;
    transition: 0.3s;
    border-radius: 50%;
}

.k-switch input:checked + .k-switch-slider {
    background-color: #3b82f6;
}

.k-switch input:checked + .k-switch-slider:before {
    transform: translateX(1.25rem);
}

/* Botones modernos */
.k-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.5;
    text-align: center;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}

.k-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.k-btn:active {
    transform: translateY(0);
}

.k-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.k-btn-primary {
    background-color: #3b82f6;
    color: #ffffff;
}

.k-btn-primary:hover {
    background-color: #2563eb;
}

.k-btn-secondary {
    background-color: #6b7280;
    color: #ffffff;
}

.k-btn-secondary:hover {
    background-color: #4b5563;
}

.k-btn-success {
    background-color: #10b981;
    color: #ffffff;
}

.k-btn-success:hover {
    background-color: #059669;
}

.k-btn-danger {
    background-color: #ef4444;
    color: #ffffff;
}

.k-btn-danger:hover {
    background-color: #dc2626;
}

.k-btn-outline {
    background-color: transparent;
    border: 2px solid #3b82f6;
    color: #3b82f6;
}

.k-btn-outline:hover {
    background-color: #3b82f6;
    color: #ffffff;
}

/* Tamaños de botones */
.k-btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
}

.k-btn-lg {
    padding: 1rem 2rem;
    font-size: 1.125rem;
}

.k-btn-block {
    display: flex;
    width: 100%;
}

/* Form layout */
.k-form-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.k-form-col {
    flex: 1;
}

@media (max-width: 768px) {
    .k-form-row {
        flex-direction: column;
    }
}

/* Fieldset moderno */
.k-fieldset {
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.k-legend {
    font-size: 1.125rem;
    font-weight: 600;
    color: #111827;
    padding: 0 0.5rem;
}

/* File input moderno */
.k-file-input {
    display: block;
    width: 100%;
    padding: 0.75rem;
    border: 2px dashed #d1d5db;
    border-radius: 0.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.k-file-input:hover {
    border-color: #3b82f6;
    background-color: #eff6ff;
}

/* Input con contador de caracteres */
.k-input-counter {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
}

/* Validación en tiempo real */
.k-input.k-validating {
    border-color: #f59e0b;
}

.k-input.k-valid {
    border-color: #10b981;
}

.k-input.k-invalid {
    border-color: #ef4444;
}

/* Loading state */
.k-input-loading {
    position: relative;
}

.k-input-loading::after {
    content: "";
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    width: 1rem;
    height: 1rem;
    border: 2px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: k-spin 0.6s linear infinite;
}

@keyframes k-spin {
    to { transform: translateY(-50%) rotate(360deg); }
}
""")
    
    return "\n".join(css)


if __name__ == "__main__":
    print(generate_form_utilities())

