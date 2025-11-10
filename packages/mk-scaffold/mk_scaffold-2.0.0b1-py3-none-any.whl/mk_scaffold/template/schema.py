import cerberus

# https://docs.python-cerberus.org/en/stable/validation-rules.html
SCHEMA = r"""
---
actions:
  type: list
  default: []
  schema:
    type: dict
    default: {}
    nullable: true
    schema:
      # actions.hidden
      # --------------
      action:
        type: string
        required: True
        allowed: ["move", "remove", "remove-trailing-newline"]

      # actions.dst
      # -----------
      dst:
        type: string
        excludes: ["path"]

      # actions.else
      # ------------
      else:
        type: string
        allowed: ["remove"]

      # actions.if
      # ----------
      if:
        type: [string, boolean]
        required: True

      # actions.order
      # -------------
      order:
        type: integer
        default: 0

      # actions.path
      # ------------
      path:
        type: [string, list]
        excludes: ["dst", "src"]

      # actions.src
      # -----------
      src:
        type: string
        excludes: ["path"]

answers:
  type: dict
  default: {}

inherit:
  type: list
  default: []
  schema:
    type: dict
    default: {}
    nullable: true

    schema:
      # inherit.branch
      # --------------
      branch:
        type: string
        nullable: True

      # inherit.include
      # ---------------
      include:
        type: string
        required: true

      # inherit.filename
      # ---------------
      filename:
        type: string
        default: "scaffold.yml"

jinja2:
  type: dict
  default: {}
  schema:
    # lstrip_blocks
    lstrip_blocks:
      type: boolean
      default: false

    # trim_blocks
    trim_blocks:
      type: boolean
      default: false

questions:
  type: list
  default: []
  schema:
    type: dict
    default: {}
    nullable: true
    schema:

      # questions.description
      # ---------------------
      description:
        type: string

      # questions.hidden
      # ----------------
      hidden:
        type: [string, boolean]
        default: false

      # questions.order
      # ----------------
      order:
        type: integer
        default: 0

      # questions.name
      # --------------
      name:
        type: string
        regex: '^\S+$'
        required: true
        minlength: 1

      # questions.order
      # ---------------
      order:
        type: integer
        nullable: True

      # questions.schema
      # ----------------
      schema:
        type: dict
        nullable: true
        coerce: asdict
        check_with: schema_rules
        schema:

          # questions.schema.allowed
          # ------------------------
          allowed:
            type: list
            schema:
              type: [string, integer]

          # questions.schema.default
          # ------------------------
          default:
            type: [string, boolean, integer]

          # questions.schema.nullable
          # -------------------------
          nullable:
            type: boolean
            default: False

          # questions.schema.min_length
          # ---------------------------
          min_length:
            type: integer
            min: 1

          # questions.schema.type
          # ---------------------
          type:
            type: string
            default: "string"
            allowed: ["string", "integer", "boolean"]

"""


class LocalValidator(cerberus.Validator):
    def _normalize_coerce_asdict(self, value):
        if value is None:
            return {}
        return value

    def _check_with_schema_rules(self, field, schema):
        pass

    # TODO: Validations
