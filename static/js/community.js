// Community Functionality

let currentCategory = 'all';

// Load posts
async function loadPosts(category = 'all') {
    currentCategory = category;
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(category) || 
            (category === 'all' && btn.textContent === 'All Posts')) {
            btn.classList.add('active');
        }
    });
    
    try {
        const posts = await CommunityAPI.getPosts(category);
        displayPosts(posts);
    } catch (error) {
        console.error('Failed to load posts:', error);
        showToast('Failed to load community posts', 'error');
    }
}

// Display posts
function displayPosts(posts) {
    const container = document.getElementById('postsContainer');
    container.innerHTML = '';
    
    if (!posts || posts.length === 0) {
        container.innerHTML = '<p class="text-muted">No posts yet. Be the first to share!</p>';
        return;
    }
    
    posts.forEach(post => {
        const postCard = createPostCard(post);
        container.appendChild(postCard);
    });
}

// Create post card element
function createPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    
    card.innerHTML = `
        <div class="post-header">
            <div>
                <h3 class="post-title">${post.title}</h3>
                <div class="post-meta">
                    <span>${post.author_name}</span>
                    <span>•</span>
                    <span>${formatDate(post.created_at)}</span>
                </div>
            </div>
        </div>
        <div class="post-content">
            ${post.content}
        </div>
        <div class="post-actions">
            <button class="post-action-btn ${post.liked ? 'liked' : ''}" onclick="toggleLike('${post.id}', this)">
                <span class="material-icons">favorite</span>
                <span>${post.likes}</span>
            </button>
            <button class="post-action-btn" onclick="showComments('${post.id}')">
                <span class="material-icons">comment</span>
                <span>${post.comments_count}</span>
            </button>
        </div>
    `;
    
    return card;
}

// Toggle like on a post
async function toggleLike(postId, button) {
    if (STATE.isGuest) {
        showToast('Please login to like posts', 'warning');
        return;
    }
    
    try {
        const isLiked = button.classList.contains('liked');
        
        if (isLiked) {
            await CommunityAPI.unlikePost(postId);
            button.classList.remove('liked');
        } else {
            await CommunityAPI.likePost(postId);
            button.classList.add('liked');
        }
        
        // Update like count
        const countSpan = button.querySelector('span:last-child');
        const currentCount = parseInt(countSpan.textContent);
        countSpan.textContent = isLiked ? currentCount - 1 : currentCount + 1;
        
    } catch (error) {
        console.error('Failed to toggle like:', error);
        showToast('Failed to update like', 'error');
    }
}

// Show create post modal
function showCreatePost() {
    if (STATE.isGuest) {
        showToast('Please login to create posts', 'warning');
        return;
    }
    
    // Create modal HTML
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Create New Post</h2>
            <form id="createPostForm">
                <div class="form-group">
                    <input type="text" id="postTitle" placeholder="Title" required>
                </div>
                <div class="form-group">
                    <textarea id="postContent" placeholder="Share your thoughts..." rows="5" required></textarea>
                </div>
                <div class="form-group">
                    <select id="postCategory">
                        <option value="general">General</option>
                        <option value="support">Support</option>
                        <option value="stories">Stories</option>
                        <option value="tips">Tips</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="postAnonymous">
                        Post anonymously
                    </label>
                </div>
                <div style="display: flex; gap: 16px; justify-content: flex-end;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal(this)">Cancel</button>
                    <button type="submit" class="btn btn-primary">Post</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Handle form submission
    document.getElementById('createPostForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const title = document.getElementById('postTitle').value;
        const content = document.getElementById('postContent').value;
        const category = document.getElementById('postCategory').value;
        const anonymous = document.getElementById('postAnonymous').checked;
        
        try {
            await CommunityAPI.createPost(title, content, category, anonymous);
            showToast('Post created successfully!', 'success');
            closeModal(modal);
            loadPosts(currentCategory);
        } catch (error) {
            console.error('Failed to create post:', error);
            showToast('Failed to create post', 'error');
        }
    });
}

// Show comments modal
async function showComments(postId) {
    try {
        const comments = await CommunityAPI.getComments(postId);
        
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>Comments</h2>
                <div id="commentsList">
                    ${comments.length === 0 ? '<p class="text-muted">No comments yet</p>' : ''}
                    ${comments.map(comment => `
                        <div class="comment">
                            <div class="comment-header">
                                <span>${comment.author_name}</span>
                                <span class="text-muted">${formatDate(comment.created_at)}</span>
                            </div>
                            <div class="comment-content">${comment.content}</div>
                        </div>
                    `).join('')}
                </div>
                ${!STATE.isGuest ? `
                    <div class="add-comment">
                        <textarea id="newComment" placeholder="Add a comment..." rows="3"></textarea>
                        <button class="btn btn-primary" onclick="addComment('${postId}')">Comment</button>
                    </div>
                ` : '<p class="text-muted">Login to add comments</p>'}
                <button class="btn btn-secondary" onclick="closeModal(this)">Close</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('Failed to load comments:', error);
        showToast('Failed to load comments', 'error');
    }
}

// Add comment
async function addComment(postId) {
    const content = document.getElementById('newComment').value.trim();
    if (!content) return;
    
    try {
        await CommunityAPI.addComment(postId, content);
        showToast('Comment added!', 'success');
        
        // Refresh comments
        const modal = document.querySelector('.modal');
        if (modal) {
            closeModal(modal);
        }
        showComments(postId);
        
    } catch (error) {
        console.error('Failed to add comment:', error);
        showToast('Failed to add comment', 'error');
    }
}

// Close modal
function closeModal(element) {
    const modal = element.closest('.modal') || element;
    modal.remove();
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
    
    return date.toLocaleDateString();
}