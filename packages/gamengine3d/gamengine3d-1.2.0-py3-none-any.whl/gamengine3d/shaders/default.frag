
#version 330

struct Light {
    vec3 position;
    vec3 color;
    float intensity;
};

#define MAX_LIGHTS 8
uniform int num_lights;
uniform Light lights[MAX_LIGHTS];
uniform float ambient;

in vec3 frag_pos;
in vec3 frag_normal;
in vec3 frag_color;

out vec4 f_color;

void main() {
    vec3 normal = normalize(frag_normal);
    vec3 color = frag_color / 255.0;  // <-- convert vertex color to 0-1
    vec3 result = ambient * color;

    for (int i = 0; i < num_lights; i++) {
        vec3 light_dir = normalize(lights[i].position - frag_pos);
        float diff = max(dot(normal, light_dir), 0.0);
        result += diff * lights[i].intensity * lights[i].color * color;
    }

    f_color = vec4(result, 1.0);
}
