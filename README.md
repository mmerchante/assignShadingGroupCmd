assignShadingGroupCmd
=====================

A Maya API command that assigns a shading group to a collection of shapes.

An exercise for learning Maya's API; python is chosen due to its portability.
The equivalent MEL script would be:

```
string $sg[] = `ls -sl -sets`;

if(size($sg) == 1)
	sets -fe $sg[0] `ls -sl -transforms`;
```
