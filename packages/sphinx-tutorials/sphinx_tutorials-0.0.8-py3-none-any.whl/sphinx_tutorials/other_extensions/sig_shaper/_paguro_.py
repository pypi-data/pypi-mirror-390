
# from sphinx import addnodes
# #
# #
# # def hide_paguro_check_type_value(app, domain, objtype, contentnode):
# #     """Shorten paguro.validation.vcol → paguro.vcol, keep 'V' badge, hide Variables section."""
# #     if domain != "py" or objtype != "data":
# #         return
# #
# #     desc = contentnode.parent
# #     if not isinstance(desc, addnodes.desc):
# #         return
# #
# #     for sig in desc.findall(addnodes.desc_signature):
# #         module = sig.get("module", "")
# #         fullname = sig.get("fullname", "")
# #         full_name = f"{module}.{fullname}".strip(".")
# #         if full_name != "paguro.validation.vcol":
# #             continue
# #
# #         print(f"[hide_paguro_check_type_value] cleaning up for {full_name}")
# #
# #         # --- Make sure the grouping header doesn't get "V Variables" ---
# #         desc["objtype"] = "attribute"  # affects section grouping
# #         sig["objtype"] = "data"  # keeps the per-item 'V' badge
# #
# #         # --- Shorten displayed prefix ---
# #         sig["module"] = "paguro"
# #         sig["fullname"] = "vcol"
# #
# #         # Remove the existing dotted prefix ('paguro.validation.')
# #         for child in list(sig.findall(addnodes.desc_addname)):
# #             sig.remove(child)
# #
# #         # Insert our new short prefix ('paguro.')
# #         sig.insert(0, addnodes.desc_addname("", "paguro."))
# #
# #         # --- Remove any trailing nodes after variable name (like type/value) ---
# #         found_name = False
# #         for child in list(sig.children):
# #             if isinstance(child, addnodes.desc_name):
# #                 found_name = True
# #                 continue
# #             if found_name:
# #                 sig.remove(child)
# #
# #
# # def setup(app):
# #     app.connect("object-description-transform", hide_paguro_check_type_value,
# #                 priority=1000)
#
#
# # def hide_paguro_check_type_value(app, domain, objtype, contentnode):
# #     if domain != "py" or objtype != "data":
# #         return
# #
# #     desc = contentnode.parent
# #     if not isinstance(desc, addnodes.desc):
# #         return
# #
# #     for sig in desc.findall(addnodes.desc_signature):
# #         full_name = f"{sig.get('module', '')}.{sig.get('fullname', '')}".strip(".")
# #         if full_name != "paguro.vcol":
# #             continue
# #
# #         print(f"[hide_paguro_check_type_value] stripping nodes for {full_name}")
# #
# #         # We’ll delete every child node *after* the variable name
# #         found_name = False
# #         for child in list(sig.children):
# #             # desc_name is the actual variable name (“check”)
# #             if isinstance(child, addnodes.desc_name):
# #                 found_name = True
# #                 continue
# #             if found_name:
# #                 print(
# #                     f"   removing node type={type(child).__name__} text={child.astext()!r}")
# #                 sig.remove(child)
# #
# #
# # def setup(app):
# #     app.connect("object-description-transform", hide_paguro_check_type_value,
# #                 priority=1000)
#
#
# from sphinx import addnodes
# from docutils import nodes
#
#
# def hide_paguro_check_type_value(app, domain, objtype, contentnode):
#     """
#     Keep 'V' badge; display 'paguro.vcol' instead of 'paguro.validation.vcol';
#     remove trailing type/value nodes. Do NOT change signature attributes.
#     """
#     if domain != "py" or objtype != "data":
#         return
#
#     desc = contentnode.parent
#     if not isinstance(desc, addnodes.desc):
#         return
#
#     for sig in desc.findall(addnodes.desc_signature):
#         # Determine the fully-qualified name from attributes (do not modify them)
#         module = sig.get("module", "")
#         fullname = sig.get("fullname", "")
#         full_name = f"{module}.{fullname}".strip(".")
#         if full_name not in (
#                 "paguro.validation.vcol",
#                 "paguro.validation.vframe",
#                 "paguro.validation.vrelations",
#         ):
#             continue
#
#         # 1) Rewrite only the visible dotted prefix text (desc_addname)
#         #    Keep attributes untouched so the 'V' badge logic remains intact.
#         rewritten = False
#         for add in list(sig.findall(addnodes.desc_addname)):
#             text = add.astext()
#             if "paguro.validation." in text:
#                 add.clear()
#                 add += addnodes.desc_addname("",
#                                              text.replace("paguro.validation.",
#                                                           "paguro."))
#                 rewritten = True
#
#         # If there was no addname (rare), synthesize a short prefix before the name
#         if not rewritten:
#             # insert before the first desc_name if present
#             for i, child in enumerate(sig.children):
#                 if isinstance(child, addnodes.desc_name):
#                     sig.insert(i, addnodes.desc_addname("", "paguro."))
#                     break
#
#         # 2) Remove all nodes after the variable name (type/value annotations, etc.)
#         seen_name = False
#         for child in list(sig.children):
#             if isinstance(child, addnodes.desc_name):
#                 seen_name = True
#                 continue
#             if seen_name:
#                 sig.remove(child)
#
#
# RENAMES = {
#     "paguro.validation.valid_column.VCol": "paguro.vcol",
#     "paguro.validation.valid_column.VCol.__call__": "paguro.vcol",
#     "paguro.vcol.__call__": "paguro.vcol",
#
#     "paguro.validation.valid_frame.VFrame": "paguro.vframe",
#     "paguro.validation.valid_frame.VFrame.__call__": "paguro.vframe",
#     "paguro.vframe.__call__": "paguro.vframe",
#
#     "paguro.validation.valid_relations.VRelations": "paguro.vrelations",
#     "paguro.validation.valid_relations.VRelations.__call__": "paguro.vrelations",
#     "paguro.vrelations.__call__": "paguro.vrelations",
#
# }
#
#
# def rename_vcol_and_members(app, domain, objtype, contentnode):
#     """Rename paguro.validation.valid_column.VCol → paguro.vcol
#     and remove any 'class' prefix both from markup and from sig_prefix."""
#     if domain != "py":
#         return
#
#     desc = contentnode.parent
#     if not isinstance(desc, addnodes.desc):
#         return
#
#     for sig in desc.findall(addnodes.desc_signature):
#         module = sig.get("module", "")
#         fullname = sig.get("fullname", "")
#         full_name = f"{module}.{fullname}".strip(".")
#
#         new_prefix = None
#         for old, new in RENAMES.items():
#             if full_name == old or full_name.startswith(old + "."):
#                 new_prefix = new + full_name[len(old):]
#                 break
#
#         if not new_prefix:
#             continue
#
#         print(f"[DEBUG] Matched {full_name} → {new_prefix}")
#
#         # 🔹 remove automatic "class " prefix added by Sphinx
#         if "sig_prefix" in sig:
#             del sig["sig_prefix"]
#             print("[DEBUG] Cleared sig_prefix='class '")
#
#         # 🔹 remove <em class="property">class</em>
#         for em in list(sig.findall(nodes.emphasis)):
#             if "property" in em.get("classes", []) and "class" in em.astext():
#                 em.parent.remove(em)
#                 print("[DEBUG] Removed <em class='property'>class</em>")
#
#         # 🔹 rebuild visible name
#         for child in list(sig.children):
#             if isinstance(child, (addnodes.desc_addname, addnodes.desc_name)):
#                 sig.remove(child)
#
#         if "." in new_prefix:
#             prefix, name = new_prefix.rsplit(".", 1)
#             sig.insert(0, addnodes.desc_name("", name))
#             sig.insert(0, addnodes.desc_addname("", prefix + "."))
#         else:
#             sig.insert(0, addnodes.desc_name("", new_prefix))
#
#         sig["module"] = new_prefix.rsplit(".", 1)[0]
#         sig["fullname"] = new_prefix.rsplit(".", 1)[-1]
#
#
# def setup(app):
#     app.connect(
#         "object-description-transform",
#         hide_paguro_check_type_value,
#         priority=1000
#     )
#
#     app.connect(
#         "object-description-transform",
#         rename_vcol_and_members,
#         priority=1000
#     )
#     # app.add_config_value('raw_enabled', True, 'env')
#
#     return {"version": "1.0", "parallel_read_safe": True}
