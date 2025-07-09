const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const toggleButton = document.getElementById('toggleSidebar');

let isOpen = true;

toggleButton.addEventListener('click', () => {
  isOpen = !isOpen;

  if (isOpen) {
    sidebar.classList.remove('sidebar-collapsed');
    mainContent.classList.remove('content-shift-collapsed');
    mainContent.classList.add('content-shift');
  } else {
    sidebar.classList.add('sidebar-collapsed');
    mainContent.classList.remove('content-shift');
    mainContent.classList.add('content-shift-collapsed');
  }
});

    