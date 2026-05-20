expected schema
```
<project>
    - item_db
        - item_desc_tab
            - _id_
            - item_name (asc, unique)
            - m_time (asc)
            - item_desc (not in index)
            - url (not in index)
        - item_desc_tab_temp
            - _id_
            - item_name (asc, unique)
            - item_desc (not in index)
            - url (not in index)
            - remarks (not in index)
```