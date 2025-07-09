const modal = document.getElementById("roomModal");
  const btn = document.getElementById("addRoomBtn");
  const span = document.querySelector(".close");

  btn.onclick = function () {
    modal.style.display = "block";
  };

  span.onclick = function () {
    modal.style.display = "none";
  };

  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
    if (event.target == editModal) {
      editModal.style.display = "none";
    }
  };

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
  

 // Edit Modal Logic
const editModal = document.getElementById("editRoomModal");
const editClose = document.getElementById("editClose");

document.querySelectorAll(".editBtn").forEach(button => {
    button.addEventListener("click", () => {
        // Populate the modal with current room data
        document.getElementById("editRoomId").value = button.dataset.id;
        document.getElementById("edit_room_type").value = button.dataset.room_type;
        document.getElementById("edit_floor").value = button.dataset.floor;
        document.getElementById("edit_description").value = button.dataset.description;
        document.getElementById("edit_price").value = button.dataset.price;
        document.getElementById("edit_status").value = button.dataset.status;
        
        // Set the form action URL for the room edit
        document.getElementById("editRoomForm").action = `/edit_room/${button.dataset.id}`;
        
        // Show the modal
        editModal.style.display = "block";
    });
});

editClose.onclick = function () {
    editModal.style.display = "none";
};

// Close the modal if clicked outside of it
window.onclick = function (event) {
    if (event.target == editModal) {
        editModal.style.display = "none";
    }
};
