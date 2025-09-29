# Google Engineering Practices Documentation (GitHub Adaptation)

> This is an adaptation of the original [Google's Code Review Guidelines](https://google.github.io/eng-practices/review/), to use GitHub specific terminology. Google has their own internal tools for version control ([Piper](https://en.wikipedia.org/wiki/Piper_(source_control_system))) and code review ([Critique](https://abseil.io/resources/swe-book/html/ch19.html)). They have their own terminology, like "Change List" (CL) instead of "Pull Request" (PR) which most developers are more familiar with. The changes are minimal and the content is kept as close to the original as possible. The hope is to make this gem accessible to a wider audience.

You can run `uv run scripts/merge_docs.py` to merge the documents into a single file:

```bash
uv run scripts/merge_docs.py
```

---

Google has many generalized engineering practices that cover all languages and
all projects. These documents represent our collective experience of various
best practices that we have developed over time. It is possible that open source
projects or other organizations would benefit from this knowledge, so we work to
make it available publicly when possible.

Currently this contains the following documents:

*   [Google's Code Review Guidelines](review/index.md), which are actually two
    separate sets of documents:
    *   [The Code Reviewer's Guide](review/reviewer/index.md)
    *   [The PR Author's Guide](review/developer/index.md)

## Terminology

There is some Google-internal terminology used in some of these documents, which
we clarify here for external readers:

*   **PR (Pull Request)**: On GitHub, read all references to "CL" in these
    documents as "PR".
*   **Approve**: On GitHub, reviewers should use the formal "Approve" action in
    a PR review (equivalent to saying "LGTM").
*   **CODEOWNERS**: Where these docs mention an OWNERS file, use GitHub's
    `.github/CODEOWNERS` for code ownership and auto review requests.

## License

The documents in this project are licensed under the
[CC-By 3.0 License](LICENSE), which encourages you to share these documents. See
<https://creativecommons.org/licenses/by/3.0/> for more details.

<a rel="license" href="https://creativecommons.org/licenses/by/3.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/3.0/88x31.png" /></a>
