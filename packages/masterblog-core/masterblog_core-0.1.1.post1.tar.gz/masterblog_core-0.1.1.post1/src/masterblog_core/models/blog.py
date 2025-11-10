"""Provide the Blog class."""
from masterblog_core.models.post import Post
from masterblog_core.storage import read_json_file, write_json_file, get_next_id, save_id_to_sequence


class Blog:
    """Manage a collection of blog posts."""

    def __init__(self, blog_file_path, seq_file_path, blog_data: list = None):
        """Initialize a Blog instance."""
        self.blog_file_path = blog_file_path
        self.seq_file_path = seq_file_path
        self.posts = None
        self._ensure_persistent_storage(blog_file_path, seq_file_path)
        self.load_blog(blog_data)

    def _ensure_persistent_storage(self, blog_file_path, seq_file_path):
        """Create JSON files if they don't exist."""
        if not blog_file_path.exists():
            data = []
            write_json_file(blog_file_path, data, create_missing=True)
        if not seq_file_path.exists():
            data = {"post": 0}
            write_json_file(seq_file_path, data, create_missing=True)

    def get(self, post_id):
        """Return a single post object by its id or None if no matching was found."""
        return next((post for post in self.posts if post.get_id() == post_id), None)

    def get_posts(self):
        """Return all posts as a list of dictionaries."""
        return [post.get() for post in self.posts]

    def add(self, post: dict | Post = None, **kwargs):
        """Add a post to the collection.

        Input:
            - post object instance
            - post as dictionary
            - post as key-word arguments
        """
        # -------------------------------------------------------------
        # Reference given or create new Post instance
        if isinstance(post, Post):
            new_post = post
        elif isinstance(post, dict):
            new_post = Post(**post)
        else:
            new_post = Post(**kwargs)
        # -------------------------------------------------------------
        # Auto increment id for new post and update sequence
        next_id = get_next_id(self.seq_file_path, "post")
        new_post.set_id(next_id)
        self.posts.append(new_post)
        save_id_to_sequence(self.seq_file_path, "post", new_post.get_id())
        self.save_blog()
        return self.get(next_id)

    def update(self, post_id=None, post_object=None, **kwargs):
        """Update a post in the collection.

        Accepted input:
            - post id or post object instance
            - key-word arguments providing updated fields
            - ...or a dictionary passed as **dictionary instead
        """
        # Validate input
        if post_id is None and post_object is None:
            raise TypeError("Missing argument: post_object or post_id.")
        # Use existing post object or get one from post id
        if post_object is None:
            post_object = self.get(post_id)
        # Update post and save blog posts
        post_object.update(**kwargs)
        self.save_blog()

    def like(self, post_id=None, post_object=None):
        """Like a post in the collection.

        Accepted input:post id or post object instance
        """
        # Validate input
        if post_id is None and post_object is None:
            raise TypeError("Missing argument: post_object or post_id.")
        # Use existing post object or get one from post id
        if post_id is not None and post_object is None:
            post_object = self.get(post_id)
        # Like post and save blog posts
        post_object.like()
        self.save_blog()

    def delete(self, post):
        """Delete the given post from the collection."""
        self.posts.remove(post)
        self.save_blog()

    def save_blog(self):
        """Save the current collection of posts persistently."""
        write_json_file(self.blog_file_path, self.get_posts())

    def load_blog(self, blog_data: list = None):
        """Load blog data from argument or persistent storage."""
        if blog_data is None:
            blog_data = read_json_file(self.blog_file_path)
        self.posts = [Post(**item) for item in blog_data]


def main():
    """Main function for testing."""


if __name__ == "__main__":
    main()
