# utils.py
import os

def copy_template(env, template_name, target_path, include_dashboard=None):
    template = env.get_template(template_name)
    context = {
        "bot_file": os.path.basename("bot.py"),
        "include_dashboard": include_dashboard
    }
    content = template.render(**context)
    with open(target_path, "w") as file:
        file.write(content)