(require_directive_multi
  "require" @structure.anchor
  ("(") @structure.open
  (")") @structure.close
)

(exclude_directive_multi
  "exclude" @structure.anchor
  ("(") @structure.open
  (")") @structure.close
)

(module_directive
  "module" @structure.anchor
  ("(") @structure.open
  (")") @structure.close
)

(replace_directive_multi
  "replace" @structure.anchor
  ("(") @structure.open
  (")") @structure.close
)

(retract_directive_multi
  "retract" @structure.anchor
  ("(") @structure.open
  (")") @structure.close
)

(ignore_directive_multi
  "ignore" @structure.anchor
  ("(") @structure.open
  (")") @structure.close
)

(godebug_directive_multi
  "godebug" @structure.anchor
  ("(") @structure.open
  (")") @structure.close
)
