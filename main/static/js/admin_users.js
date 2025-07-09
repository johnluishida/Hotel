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
// Open modal
document.getElementById("addusersBtn").addEventListener("click", function () {
  document.getElementById("addUserModal").style.display = "block";
});

// Close modal
document.getElementById("closeModal").addEventListener("click", function () {
  document.getElementById("addUserModal").style.display = "none";
});

// Click outside modal
window.onclick = function (event) {
  const modal = document.getElementById("addUserModal");
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

// Toggle password visibility
function togglePassword() {
  const field = document.getElementById("passwordField");
  const icon = document.getElementById("toggleIcon");
  if (field.type === "password") {
    field.type = "text";
    icon.classList.remove('bx-show');
    icon.classList.add('bx-hide');
  } else {
    field.type = "password";
    icon.classList.remove('bx-hide');
    icon.classList.add('bx-show');
  }
}
  // Edit modal handlers
  const editButtons = document.querySelectorAll(".editBtn");
  const editModal = document.getElementById("editUserModal");
  const closeEditModal = document.getElementById("closeEditModal");

  editButtons.forEach(button => {
    button.addEventListener("click", () => {
      document.getElementById("editUserId").value = button.getAttribute("data-id");
      document.getElementById("editUsername").value = button.getAttribute("data-username");
      document.getElementById("editName").value = button.getAttribute("data-name");
      document.getElementById("editEmail").value = button.getAttribute("data-email");
      document.getElementById("editPhone").value = button.getAttribute("data-phone");
      document.getElementById("editAddress").value = button.getAttribute("data-address");
      document.getElementById("editAge").value = button.getAttribute("data-age");

      editModal.style.display = "block";
    });
  });

  closeEditModal.addEventListener("click", () => {
    editModal.style.display = "none";
  });

  window.onclick = function (event) {
    if (event.target == editModal) {
      editModal.style.display = "none";
    }
  };

