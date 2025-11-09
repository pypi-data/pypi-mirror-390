
#version 330

in vec3 in_vert;
in vec3 in_color;
in vec3 in_normal;

out vec3 frag_pos;
out vec3 frag_normal;
out vec3 frag_color;

uniform mat4 mvp;
uniform mat4 model;  // optional if you want model transforms

void main() {
    frag_pos = vec3(model * vec4(in_vert, 1.0));  // world space position
    frag_normal = mat3(transpose(inverse(model))) * in_normal; // transform normal
    frag_color = in_color;
    gl_Position = mvp * vec4(in_vert, 1.0);
}
