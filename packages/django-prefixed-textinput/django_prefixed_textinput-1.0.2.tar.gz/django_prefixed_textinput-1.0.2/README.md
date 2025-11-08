# django-prefixed-textinput

An extension of the default `TextInput` widget that displays a read-only string prefix over the input field.

![Screenshot showing widget in the Django admin](/images/screenshot.png)

## Compatibility

The widget has been tested on all Python/Django version combinations [officially supported](https://docs.djangoproject.com/en/5.2/faq/install/#what-python-version-can-i-use-with-django) by the Django project:

|                | Django 4.2 | 5.0 | 5.1 | 5.2 |
|---------------:|:----------:|:---:|:---:|:---:|
| **Python 3.8** | ✔          |     |     |     |
| **3.9**        | ✔          |     |     |     |
| **3.10**       | ✔          | ✔   | ✔   | ✔   |
| **3.11**       | ✔          | ✔   | ✔   | ✔   |
| **3.12**       | ✔          | ✔   | ✔   | ✔   |
| **3.13**       |            |     | ✔   | ✔   |
| **3.14**       |            |     |     | ✔   |

If you need to use `django-prefixed-textinput` with Django 3, please use a version of the package prior to `1.0.0`.

Styling for the widget includes support for right-to-left (RTL) languages so this should work more or less as expected. Note that IE11 is **not** supported as the widget styling requires support for [CSS Custom Properties](https://caniuse.com/css-variables) ("CSS Variables").

## Installation

```
$ pip install django-prefixed-textinput
```

## Usage

Add `prefixed_textinput` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    # ...
    'prefixed_textinput',
]
```

Import the widget:

```python
from prefixed_textinput import PrefixedTextInput
```

Define a custom admin form, which allows overriding the widget for a specific field:

```python
# forms.py
from django import forms
from prefixed_textinput import PrefixedTextInput


class MyModelAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'myfield':
                PrefixedTextInput(prefix='FOO'),
        }
        fields = '__all__'
```

Specify the custom admin form in your admin definition:

```python
# admin.py
from django import admin

from .forms import MyModelAdminForm
from .models import MyModel


@admin.register(MyModel)
class ProductAdmin(admin.ModelAdmin):
    form = MyModelAdminForm
```

## Development

If working locally on the package you can install the development tools via `pip`:

```shell
$ pip install -e .[dev]
```

Run the bundled Django example project:

```shell
$ cd example_project
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver 0.0.0.0:8000
$ open http://localhost:8000/admin/
```

Navigate to the example `Book` model in the `Bookshop` app to see the widget in action.

Run the extremely basic test suite across environments using `tox`:

```shell
$ tox run
```

## Issues, Suggestions, Contributions

...are welcome on GitHub. Thanks for your interest in `django-prefixed-textinput`!
