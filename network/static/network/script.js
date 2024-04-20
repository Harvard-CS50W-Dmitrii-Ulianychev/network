// Get the CSRF token from the Django CSRF cookie
const csrftoken = Cookies.get('csrftoken');

function followUser(userId) {

  const formData = new FormData();
  formData.append('user_id', userId.toString());

  fetch('/follow', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken,
    },
    body: formData,
  })
  .then(response => {
    console.log('response:', response);
    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('data:', data);
    if (data.success) {
      const button = document.querySelector(`#follow-button-${userId}`);
      if (data.following) {
        let element = document.querySelector('#followers-count')
        let followersCount = parseInt(element.innerHTML, 10)
        element.innerHTML = followersCount + 1
        button.textContent = 'Unfollow';
      } else {
        let element = document.querySelector('#followers-count')
        let followersCount = parseInt(element.innerHTML, 10)
        element.innerHTML = followersCount - 1
        button.textContent = 'Follow';
      }
    } else {
      console.error('Failed to follow user:', data);
    }
  })
  .catch(error => {
    console.error('Error following user:', error);
  });
}

function likeUnlikePost(postId, likeElement) {
  console.log('likeUnlikePost called with postId:', postId);

  const formData = new FormData();
  formData.append('post_id', postId.toString());

  fetch('/like-unlike', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken,
    },
    body: formData,
  })
  .then(response => {
    console.log('response:', response);
    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('data:', data);
    if (data.success) {
      // Update the UI based on the message (liked or unliked)
      const heartIcon = likeElement.querySelector('.fas.fa-heart');
      const likeCount = likeElement.querySelector('.like-count');

      if (data.message === 'liked') {
        heartIcon.style.color = 'red';
        likeCount.textContent = parseInt(likeCount.textContent) + 1;
      } else {
        heartIcon.style.color = '#d8d9da';
        likeCount.textContent = parseInt(likeCount.textContent) - 1;
      }
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function editPost(postPk) {
  postPk = parseInt(postPk);

  var elementId = "post-content-" + postPk;
  var element = document.getElementById(elementId);
  var existingContent = element.textContent || element.innerText;

  // Create the new div
  var newDiv = document.createElement("div");

  // Create the textarea
  var textarea = document.createElement("textarea");
  textarea.classList.add("form-element-block");
  textarea.value = existingContent;
  textarea.rows = 3;
  textarea.cols = 70;
  newDiv.appendChild(textarea);

  // Create the Save button
  var saveButton = document.createElement("button");
  saveButton.classList.add("form-element-block");
  saveButton.textContent = "Save";
  saveButton.addEventListener("click", function() {
    var postContent = textarea.value;

    const formData = new FormData();
    formData.append("content", postContent);

    fetch("/edit-post/" + postPk, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrftoken,
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            // Update the DOM to reflect the saved changes or display a success message
            element.innerHTML = postContent;
        } else {
            // Display an error message
            console.log("Failure");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        // Display an error message
    });
  });
  newDiv.appendChild(saveButton);

  // Replace the existing content with the new div
  element.innerHTML = "";
  element.appendChild(newDiv);
}