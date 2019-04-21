=======
History
=======

0.1.0.3 (2019-02-08)
------------------

* Changed OptionTemplateSolver:
    * Templates resolve to actual objects, instead of their string representation
    * Templates can no longer be combined with a string outside the template.
    * Example Template: '{{'one two'.split()}}' resolves to ['one', 'two'] (array)
    * Example Invalid Template: 'The answer is {{40+2}}!' does not resolve and remains the same string.

0.1.0.2 (2019-02-08)
------------------

* New Feature: GetNeededSecrets
* minor bug fixes

0.1.0.1 (2019-02-08)
------------------

* First release on PyPI.
