# bambot/utils.py
import os

def copy_template(env, template_name, target_path):
    template = env.get_template(template_name)
    content = template.render(bot_file=os.path.basename("bot.py"))
    with open(target_path, "w") as file:
        file.write(content)