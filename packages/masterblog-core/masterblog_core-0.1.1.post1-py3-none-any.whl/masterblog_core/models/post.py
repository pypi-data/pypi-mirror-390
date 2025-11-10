"""Provide the Post class."""


class Post:
    """Represent a specific post in a blog."""

    def __init__(self, author: str, title: str, content: str, likes: int = 0, id: int = -1):
        """Create a new Post instance."""
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-positional-arguments
        # All attributes are necessary to represent a blog post
        self.id = id
        self.author = author
        self.title = title
        self.content = content
        self.likes = likes

    def get(self):
        """Return a Post instance as dictionary."""
        return self.__dict__

    def update(self, author: str = None, title: str = None, content: str = None):
        """Change author, title or content of a Post instance."""
        if author:
            self.author = author
        if title:
            self.title = title
        if content:
            self.content = content

    def like(self):
        """Increment the like value by one."""
        self.likes += 1

    def set_id(self, post_id):
        """Set id for a Post instance."""
        self.id = post_id

    def get_id(self):
        """Return id for a Post instance."""
        return self.id


def main():
    """Main function for testing."""


if __name__ == "__main__":
    main()
