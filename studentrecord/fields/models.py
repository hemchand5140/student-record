from django.db import models

class Fields(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True, default=0)
    classname = models.CharField(max_length=100, null=True, blank=True)
    marks = models.IntegerField(null=True, blank=True, default=0)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True, default='profile_pics/default.jpg')

    def __str__(self):
        return self.name

    @property
    def profile_pic_url(self):
        if self.profile_pic and hasattr(self.profile_pic, 'url'):
            return self.profile_pic.url
        # Provide a URL to a default image if no profile_pic is set or if it's missing
        # Ensure 'default.png' exists in 'media/profile_pics/' or adjust path
        return '/media/profile_pics/default.png' # Or use static asset: from django.templatetags.static import static; static('images/default.png')