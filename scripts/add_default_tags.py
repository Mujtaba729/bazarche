from bazarche_app.models import Tag

def add_default_tags():
    for name in ['نو', 'دست دوم']:
        if not Tag.objects.filter(name_fa=name).exists():
            Tag.objects.create(name_fa=name)
            print(f"Tag '{name}' created.")
        else:
            print(f"Tag '{name}' already exists.")

if __name__ == "__main__":
    add_default_tags()
