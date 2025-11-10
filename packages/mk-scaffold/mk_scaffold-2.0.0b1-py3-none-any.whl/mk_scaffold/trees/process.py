import os
import shutil


def _action_move(item, env, ctx, output_dir):
    src = str(env.from_string(item["src"]).render(**ctx))
    src = os.path.join(output_dir, src)

    dst = str(env.from_string(item["dst"]).render(**ctx))
    dst = os.path.join(output_dir, dst)
    # Ensure path is subpath
    # TODO   if not Path(dst).is_relative_to(output_dir):
    #        print(f'warning: skipping path "{dst_orig}" as it is not relative to output path.', file=sys.stderr)
    #        return

    if_ = env.from_string(item["if"]).render(**ctx)
    if if_:
        if os.path.exists(src):
            shutil.move(src, dst)
    elif item.get("else") == "remove":
        # TODO if not Path(src).is_relative_to(output_dir):
        # TODO     print(f'warning: skipping path "{src}" as it is not relative to output path.', file=sys.stderr)
        # TODO     return
        if os.path.exists(src):
            os.remove(src)


def _action_remove(item, env, ctx, output_dir):
    if_ = item["if"]
    if if_ not in [True, False]:
        if_ = env.from_string(if_).render(**ctx)
    if not if_:
        return

    for path in item["path"]:
        path = str(env.from_string(path).render(**ctx))
        path = os.path.join(output_dir, path)

        # Ensure path is subpath
        # TODOif not Path(path).is_relative_to(output_dir):
        # TODO    print(f'warning: skipping path "{path_orig}" as it is not relative to output path.', file=sys.stderr)
        # TODO    continue

        if os.path.islink(path) or os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


def _action_remove_nl(item, env, ctx, output_dir):
    """
    pipx install pre-commit-hooks
    """
    if_ = item["if"]
    if if_ not in [True, False]:
        if_ = env.from_string(if_).render(**ctx)
    if not if_:
        return

    for path in item["path"]:
        path = str(env.from_string(path).render(**ctx))
        path = os.path.join(output_dir, path)

        with open(path, encoding="UTF-8") as fd:
            data = fd.read()
        data = data.rstrip()
        with open(path, mode="w", encoding="UTF-8") as fd:
            fd.write(data)


def process(env, ctx, tpl, output_dir):
    for item in tpl.bus["actions"]:
        action = item["action"]
        if action == "move":
            _action_move(item, env, ctx, output_dir)
        elif action == "remove":
            _action_remove(item, env, ctx, output_dir)
        elif action == "remove-trailing-newline":
            _action_remove_nl(item, env, ctx, output_dir)
        else:
            assert False
