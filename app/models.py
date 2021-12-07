from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class UserType(models.Model):
    user_type_name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""
    use_in_migrations = True

    def _create_user(self, email, password, user_type_id, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email, user_type_id=UserType.objects.get(id=user_type_id), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        # user = Users.objects.update_or_create(user)
        return user

    def create_preuser(self, email, password, user_type_id, **extra_fields):
        """
            Багш group-д нэмэхэд Users дотор үүссэн хаяг дараа нь 
            оюутан өөрөө бүртгүүлэх үед ашиглагдах method
        """
        Users.objects.filter(email=email).update(user_type_id=UserType.objects.get(id=user_type_id), **extra_fields)
        user = Users.objects.get(email=email)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type_id_id', 1)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Users(AbstractUser):
    """User model."""
    username = None
    email = models.EmailField(_('email address'), unique=True)
    user_type_id = models.ForeignKey(UserType, on_delete=models.CASCADE)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()


class RatingCriteria(models.Model):
    rc_name = models.CharField(max_length=1000)
    teacher_id = models.ForeignKey(Users, on_delete=CASCADE)
    is_default = models.BooleanField()


class Group(models.Model):
    teacher_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    group_number = models.CharField(max_length=4)
    lesson_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class GroupStudents(models.Model):
    group_id = models.ForeignKey(Group, on_delete=CASCADE)
    student_id = models.ForeignKey(Users, on_delete=CASCADE)


class SubGroup(models.Model):
    subgroup_name = models.CharField(max_length=100)
    group_id = models.ForeignKey(Group, on_delete=CASCADE)
    is_active = models.BooleanField(default=True)
    deadline = models.DateField()


class TeamMember(models.Model):
    subgroup_id = models.ForeignKey(SubGroup, on_delete=CASCADE)
    group_student_id = models.ForeignKey(GroupStudents, on_delete=CASCADE)


class Ratings(models.Model):
    team_member_id = models.ForeignKey(TeamMember, on_delete=CASCADE)
    rc_name = models.CharField(max_length=1000)
    rating_value = models.IntegerField()
    comment = models.CharField(max_length=5000)
