import os
import shutil
import sys

import jinja2
from boltons import fileutils


def _clone_file(env, ctx, src, dst):
    try:
        with open(src, encoding="UTF-8") as fdr, open(dst, mode="w", encoding="UTF-8") as fdw:
            dst_contents = fdr.read()
            dst_contents = env.from_string(dst_contents).render(**ctx)
            fdw.write(str(dst_contents or ""))
        shutil.copymode(src, dst)

    except UnicodeDecodeError:
        with open(src, mode="rb") as fdr, open(dst, mode="wb") as fdw:
            dst_contents = fdr.read()
            fdw.write(dst_contents)
        shutil.copymode(src, dst)

    except jinja2.exceptions.UndefinedError as err:
        sys.exit(f'error: while rendering "{src}", encountered template error: {err}')
    except jinja2.exceptions.TemplateSyntaxError as err:
        sys.exit(f'error: while rendering "{src}", encountered template error: {err}')


def _clone(env, ctx, output_dir, template_path):
    def templatize(src, string):
        # Change templates in file name
        try:
            return str(env.from_string(string).render(**ctx))
        except jinja2.exceptions.UndefinedError as err:
            sys.exit(f'error: templating error during "{src}" file: {err}')

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    src_path = template_path
    src_path = os.path.join(src_path, "template")
    src_path = os.path.abspath(src_path)

    if not os.path.isdir(src_path):
        print(
            'warning: no "template" named folder found in source template directory. No templating can be done',
            file=sys.stderr,
        )

    for src in fileutils.iter_find_files(src_path, "*", include_dirs=True):
        dst = os.path.relpath(src, src_path)
        dst = templatize(src, dst)
        dst = os.path.join(output_dir, dst)

        if os.path.islink(src):
            target_src = os.readlink(src)
            target_dst = templatize(src, target_src)
            if target_src == target_dst:
                shutil.copyfile(src, dst, follow_symlinks=False)
            else:
                # TODO
                sys.exit("error: changing link is not implemented while handling {src}")
        elif os.path.isdir(src):
            fileutils.mkdir_p(dst)
        elif os.path.isfile(src):
            fileutils.mkdir_p(os.path.dirname(dst))
            _clone_file(env, ctx, src, dst)
        else:
            sys.exit(f'error: path copy failed. File "{src}" of unknown type')


def clone(env, ctx, tpl, output_dir):
    for item in tpl.bus["templates"]:
        # print(item)
        _clone(env, ctx, output_dir, item["template_path"])
