# pytsterrors
This package is created to validate trace calls of exceptions in unit tests.

The source code of the package is https://github.com/rm4n0s/pytsterrors

## Description
It is a new way to handle exceptions and to be able to write unit tests that will validate stack traces. <br/>
The idea came from the Odin programming language, and even though it isn't nearly as good as in Odin, it is good enough
to help me write monolithic applications or microservices without worrying about complications or accidental changes.<br/>

I have written in the past a blog post called [Error Handling Challenge](https://rm4n0s.github.io/posts/3-error-handling-challenge/), where it compares each programming language's solution of the error challenge.
For a long time, I believed that Python couldn't solve it because of exceptions.<br/>
Actually, I have proven with this package that not only does it solve it (check the 'error_challenge' folder in 'examples'), but it is simpler than the rest of programming languages.

I hope this package will help me to architect software in what I call [Can't Driven Development](https://rm4n0s.github.io/posts/6-cant-driven-development/).

Expect changes in this package, because I will start experiment its validity in other projects of mine and maybe new things will be added.


