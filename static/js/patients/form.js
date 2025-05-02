document.addEventListener('DOMContentLoaded', function() {
    // Funciones auxiliares
    function createFormGroup(label, input) {
        const group = document.createElement('div');
        group.className = 'form-group';
        
        const labelElement = document.createElement('label');
        labelElement.textContent = label;
        
        group.appendChild(labelElement);
        group.appendChild(input);
        
        return group;
    }

    function createInput(type, name, placeholder = '', value = '', required = false) {
        const input = document.createElement('input');
        input.type = type;
        input.name = name;
        input.className = 'form-input';
        input.placeholder = placeholder;
        input.value = value;
        input.required = required;
        return input;
    }

    function createRemoveButton() {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-icon btn-remove';
        button.onclick = function() {
            this.closest('.formset-item').remove();
        };
        button.innerHTML = '<span>×</span>';
        return button;
    }

    // Inicializar contadores
    let parentIndex = 0;
    let siblingIndex = 0;
    let householdIndex = 0;

    // Cargar datos existentes si están disponibles
    const existingDataElement = document.getElementById('existingData');
    if (existingDataElement) {
        const existingData = JSON.parse(existingDataElement.textContent);
        
        // Cargar padres existentes
        if (existingData.parents) {
            existingData.parents.forEach(parent => {
                window.addParent(parent);
            });
        }
        
        // Cargar hermanos existentes
        if (existingData.siblings) {
            existingData.siblings.forEach(sibling => {
                window.addSibling(sibling);
            });
        }
        
        // Cargar habitantes del hogar existentes
        if (existingData.household_members) {
            existingData.household_members.forEach(member => {
                window.addHouseholdMember(member);
            });
        }

        // Marcar opciones del historial médico
        if (existingData.medical_history) {
            Object.entries(existingData.medical_history).forEach(([key, value]) => {
                const radio = document.querySelector(`input[name="medical_${key}"][value="${value}"]`);
                if (radio) {
                    radio.checked = true;
                }
            });
        }
    }

    // Manejadores para los botones de agregar
    document.getElementById('addParentBtn')?.addEventListener('click', () => window.addParent());
    document.getElementById('addSiblingBtn')?.addEventListener('click', () => window.addSibling());
    document.getElementById('addHouseholdMemberBtn')?.addEventListener('click', () => window.addHouseholdMember());

    // Previsualización de la foto
    const photoInput = document.querySelector('input[type="file"]');
    const photoPreview = document.getElementById('photoPreview');

    if (photoInput && photoPreview) {
        photoInput.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    photoPreview.innerHTML = `<img src="${e.target.result}" alt="Vista previa">`;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
});

// Mantener las funciones window.addParent, window.addSibling y window.addHouseholdMember como están