.. role:: hidden

{{ name | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ name }}
    :members: __init__

{% if methods %}
.. rubric:: Methods

.. autosummary::
    :toctree:
    :nosignatures:

    {% for item in methods %}
    {%- if not item in inherited_members %}
    {%- if not item.startswith("_") %}
    ~{{ name }}.{{ item }}
    {%- endif %}
    {%- endif %}
    {%- endfor %}
{%- endif %}

{% if attributes %}
.. rubric:: Attributes

.. autosummary::
    :toctree:

    {% for item in attributes %}
    ~{{ name }}.{{ item }}
    {%- endfor %}
{%- endif %}
