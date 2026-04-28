// Function to render the posts
function renderPosts(posts) {
    // Get the post list container
    const stream = document.getElementById("id_post_list");

    // For each post...
    posts.forEach(post => {
        // Get the post ID from the post data
        const postId = `id_post_div_${post.id}`;
        let div = document.getElementById(postId);

        // If the post div doesn't exist, create it
        if (!div) {
            div = document.createElement("div");
            div.id = postId;

            // Set the inner HTML of the post div
            div.innerHTML = `
                <div>
                    <a 
                        id="id_post_profile_${post.id}" 
                        href="/profile/${post.author_username}">
                            ${post.author_first_name} ${post.author_last_name}
                    </a>

                    <span id="id_post_text_${post.id}">
                        ${post.text}
                    </span>

                    <span id="id_post_date_time_${post.id}">
                        ${new Date(post.created_at).toLocaleString("en-US", {
                            timeZone: "America/New_York",
                            year: "numeric",
                            month: "numeric",
                            day: "numeric",
                            hour: "numeric",
                            minute: "numeric",
                            hour12: true,
                        }).replace(",", "")}
                    </span>
                </div>

                <div>
                    <label for="id_comment_input_text_${post.id}">Comment:</label>
                    <input id="id_comment_input_text_${post.id}" type="text" value="">
                    <button id="id_comment_button_${post.id}" type="button">Submit</button>
                </div>

                <div id="id_comment_list_${post.id}"></div>
            `;
            // Prepend the new post div to the post list container
            stream.prepend(div);
        }

        // Get the comment list div
        const commentList = document.getElementById(`id_comment_list_${post.id}`);

        if (!commentList) return;

        // For each comment under a post...
        (post.comments || []).forEach(comment => {
            // Get the comment id
            const commentId = `id_comment_div_${comment.id}`;

            // Skip if comment already rendered
            if (document.getElementById(commentId)) return;

            // o.w. create comment div
            const commentDiv = document.createElement("div");
            commentDiv.id = commentId;

            // Populate the above div 
            commentDiv.innerHTML = `
                <span id="id_comment_profile_${comment.id}">
                    ${comment.author_first_name} ${comment.author_last_name}:
                </span>

                <span id="id_comment_text_${comment.id}">
                    ${comment.text}
                </span>

                <span id="id_comment_date_time_${comment.id}">
                    ${new Date(comment.created_at).toLocaleString("en-US", {
                        timeZone: "America/New_York",
                        year: "numeric",
                        month: "numeric",
                        day: "numeric",
                        hour: "numeric",
                        minute: "numeric",
                        hour12: true,
                    }).replace(",", "")}
                </span>
            `;
            
            // Append to the comment list div
            commentList.appendChild(commentDiv);
        });
    });
}


// Function to get the CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}


// Function to attach event listeners to the comment buttons
function enableCommentActions() {
    // Get all the comment buttons
    const buttons = document.querySelectorAll("[id^='id_comment_button_']");

    buttons.forEach(button => {
        // If the listener is already attached, return
        if (button.dataset.listenerAttached) return;

        // o.w. attach the listener
        button.addEventListener("click", () => {
            // Get the post ID from the button ID
            const postId = button.id.split("_").pop();
            // Get the input element
            const input = document.getElementById(`id_comment_input_text_${postId}`);
            // Get the comment text from the input element
            const commentText = input.value.trim();

            // If the comment text is empty, return
            if (!commentText) return;

            // Send the comment text to the server
            // then convert the response to JSON
            // then clear the input element
            // catch any errors and log them to the console
            fetch("/socialnetwork/add-comment", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: `post_id=${postId}&comment_text=${encodeURIComponent(commentText)}`
            })
            .then(response => response.json())
            .then(data => {
                // clear input
                input.value = "";
            
                // render instantly
                const c = data.comment;
                const commentDivId = `id_comment_div_${c.id}`;
            
                if (document.getElementById(commentDivId)) return;
            
                const commentList = document.getElementById(`id_comment_list_${postId}`);
                if (!commentList) return;
            
                const commentDiv = document.createElement("div");
                commentDiv.id = commentDivId;
            
                commentDiv.innerHTML = `
                    <span id="id_comment_profile_${c.id}">
                        ${c.author_first_name} ${c.author_last_name}:
                    </span>
            
                    <span id="id_comment_text_${c.id}">
                        ${c.text}
                    </span>
            
                    <span id="id_comment_date_time_${c.id}">
                        ${new Date(c.created_at).toLocaleString("en-US", {
                            timeZone: "America/New_York",
                            year: "numeric",
                            month: "numeric",
                            day: "numeric",
                            hour: "numeric",
                            minute: "numeric",
                            hour12: true,
                        }).replace(",", "")}
                    </span>
                `;
                commentList.appendChild(commentDiv);
            })
            .catch(error => console.log("Error:", error));
        });

        // Mark this button as having a listener attached
        button.dataset.listenerAttached = "true";
    });
}


// Function to refresh the global stream
function refreshGlobal() {
    // Fetch the global stream from the server
    // then convert the response to JSON
    // then render the posts
    // then enable the comment actions
    // catch any errors and log them to the console
    fetch("/socialnetwork/get-global")
        .then(response => response.json())
        .then(data => {
            renderPosts(data.posts);
            enableCommentActions();
        })
        .catch(error => console.log("Error:", error));
}

refreshGlobal();
setInterval(refreshGlobal, 5000);