# Reflection

1. What did static analysis reveal about this project?

   Static analysis showed a mix of functional and security issues. The most obvious problems were the mutable default list, broad exception handling, unsafe XML parsing, and unsafe archive extraction. Pylint also highlighted inconsistent naming, long lines, and missing documentation, while Bandit flagged security-sensitive patterns.

2. Which issues were the highest priority, and why?

   The highest priority issues were the unsafe tar extraction and XML parsing because they could be exploited by attackers to read or overwrite files or process malicious payloads. The insecure SSL request and hardcoded service configuration were also important because they could weaken trust and reduce safe deployment practices.

3. How did fixing these issues improve the program?

   The fixes made the code safer, more predictable, and easier to maintain. The premium calculation logic became consistent, invalid inputs were handled more cleanly, and the program no longer mutated shared state across calls. Security-sensitive file and network operations were hardened without changing the app's intended behavior.

4. Why is static analysis important in development?

   Static analysis catches problems before the software reaches production. It helps teams identify style violations, logic bugs, maintenance risks, and security weaknesses early, when they are cheaper and easier to fix. In practice, it makes code more reliable and supports better review and testing practices.
