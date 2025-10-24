from django.db import models


class AdminUser(models.Model):
    """Admin users for content management"""
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50,
                           choices=[
                               ('admin', 'Admin'),
                               ('editor', 'Editor'),
                               ('content_creator', 'Content Creator'),
                           ])
    
    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'
    
    def __str__(self):
        return f"{self.email} - {self.role}"


class Article(models.Model):
    """Articles and fitness tips"""
    title = models.CharField(max_length=255)
    content = models.TextField()
    media_url = models.URLField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100,
                               choices=[
                                   ('fitness', 'Fitness'),
                                   ('nutrition', 'Nutrition'),
                                   ('wellness', 'Wellness'),
                                   ('motivation', 'Motivation'),
                                   ('tips', 'Tips'),
                               ])
    created_by = models.ForeignKey(AdminUser, on_delete=models.CASCADE, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'articles'
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
