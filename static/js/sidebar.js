// Dropdown Toggle Function for Admin Sidebar
function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    const icon = document.getElementById(dropdownId + '-icon');
    
    if (dropdown.classList.contains('hidden')) {
        dropdown.classList.remove('hidden');
        if (icon) icon.classList.add('rotate-180');
    } else {
        dropdown.classList.add('hidden');
        if (icon) icon.classList.remove('rotate-180');
    }
}