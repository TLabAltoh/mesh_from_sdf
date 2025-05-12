
# A library of distance functions and mathematical utilities.
include_ = '''
        mat4 rotmat(vec3 axis, in float angle) {
            axis = normalize(axis);
            float s = sin(angle);
            float c = cos(angle);
            float oc = 1.0 - c;
            
            return mat4(oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
                        oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
                        oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
                        0.0,                                0.0,                                0.0,                                1.0);
        }
        
        // https://qiita.com/ukonpower/items/ebafd19fcb33f37ed273
        mat4 qua2mat( in vec4 q ){
            mat4 m = mat4(
                1.0 - 2.0 * pow( q.y, 2.0 ) - 2.0 * pow( q.z, 2.0 ), 2.0 * q.x * q.y + 2.0 * q.w * q.z, 2.0 * q.x * q.z - 2.0 * q.w * q.y, 0.0,
                2.0 * q.x * q.y - 2.0 * q.w * q.z, 1.0 - 2.0 * pow( q.x, 2.0 ) - 2.0 * pow( q.z, 2.0 ), 2.0 * q.y * q.z + 2.0 * q.w * q.x, 0.0,
                2.0 * q.x * q.z + 2.0 * q.w * q.y, 2.0 * q.y * q.z - 2.0 * q.w * q.x, 1.0 - 2.0 * pow( q.x, 2.0 ) - 2.0 * pow( q.y, 2.0 ), 0.0,
                0.0, 0.0, 0.0, 1.0
            );
            return m;
        }

        float dot2( in vec2 v ) { return dot(v,v); }
        float dot2( in vec3 v ) { return dot(v,v); }
        float ndot( in vec2 a, in vec2 b ) { return a.x*b.x - a.y*b.y; }

        float rounding( in float d, in float h )
        {
            return d - h;
        }

        //
        // No Blending
        //

        float opUnion( in float d0, in float d1 )
        {
            return min(d0,d1);
        }
        float opDifference( in float d0, in float d1 )
        {
            return max(-d0,d1);
        }
        float opIntersection( in float d0, in float d1 )
        {
            return max(d0,d1);
        }

        //
        // Smooth
        //
        
        float opSmoothUnion( in float d0, in float d1, in float k )
        {
            float h = clamp( 0.5 + 0.5*(d1-d0)/k, 0.0, 1.0 );
            return mix( d1, d0, h ) - k*h*(1.0-h);
        }
        float opSmoothDifference( in float d0, in float d1, in float k )
        {
            float h = clamp( 0.5 - 0.5*(d1+d0)/k, 0.0, 1.0 );
            return mix( d1, -d0, h ) + k*h*(1.0-h);
        }
        float opSmoothIntersection( in float d0, in float d1, in float k )
        {
            float h = clamp( 0.5 - 0.5*(d1-d0)/k, 0.0, 1.0 );
            return mix( d1, d0, h ) + k*h*(1.0-h);
        }

        // -----------------------------------------------------------------------------------------------
        // https://mercury.sexy/hg_sdf/
        //

        //
        // Round
        //
        
        float opRoundUnion( in float d0, in float d1, in float r )
        {
            vec2 u = max(vec2(r - d0, r - d1), vec2(0));
            return max(r, min (d0, d1)) - length(u);
        }
        float opRoundDifference( in float d0, in float d1, in float r )
        {
            return opRoundUnion(d0, -d1, r);
        }
        float opRoundIntersection( in float d0, in float d1, in float r )
        {
            vec2 u = max(vec2(r + d0, r + d1), vec2(0));
            return min(-r, max (d0, d1)) + length(u);
        }

        // s: champferSize
        float opChampferUnion( in float d0, in float d1, in float s) {
            const float SQRT05 = 0.70710678118;
            return min(min(d0, d1), (d0 - s + d1)*SQRT05);
        }
        float opChampferDifference( in float d0, in float d1, in float s) {
            return opChampferUnion(d0, -d1, s);
        }
        float opChampferIntersection( in float d0, in float d1, in float s) {
            const float SQRT05 = 0.70710678118;
            return max(max(d0, d1), (d0 + s + d1)*SQRT05);
        }
        
        float opStairsUnion( in float d0, in float d1, in float s, in float n) {
            float _s = s/n;
            float u = d1-_s;
            return min(min(d0,d1), 0.5 * (u + d0 + abs ((mod (u - d0 + _s, 2 * _s)) - _s)));
        }
        float opStairsDifference( in float d0, in float d1, in float s, in float n) {
            return -opStairsUnion(-d0, d1, s, n);
        }
        float opStairsIntersection( in float d0, in float d1, in float s, in float n) {
            return -opStairsUnion(-d0, -d1, s, n);
        }

        //
        // -----------------------------------------------------------------------------------------------


        float opExtrusion( in vec3 p, in float dist, in float h )
        {
            vec2 w = vec2( dist, abs(p.z) - h );
            return min(max(w.x,w.y),0.0) + length(max(w,0.0));
        }

        float sdBox( in vec3 p, in vec3 bounding, in float rounding ) {
            vec3 q = abs(p)-bounding+rounding;
            return length(max(q,0.0))+min(max(q.x,max(q.y,q.z)),0.0)-rounding;
        }
        float sdSphere( in vec3 p, in float r ) {
            return length(p)-r;
        }
        float sdCylinder( in vec3 p, in float h, in float r )
        {
            vec2 d = abs(vec2(length(p.xz),p.y)) - vec2(r,h);
            return min(max(d.x,d.y),0.0) + length(max(d,0.0));
        }
        float sdCappedCone( in vec3 p, in float h, in float r0, in float r1 )
        {
            vec2 q = vec2( length(p.xz), p.y );
            vec2 k1 = vec2(r1,h);
            vec2 k2 = vec2(r1-r0,2.0*h);
            vec2 ca = vec2(q.x-min(q.x,(q.y<0.0)?r0:r1), abs(q.y)-h);
            vec2 cb = q - k1 + k2*clamp( dot(k1-q,k2)/dot2(k2), 0.0, 1.0 );
            float s = (cb.x<0.0 && ca.y<0.0) ? -1.0 : 1.0;
            return s*sqrt( min(dot2(ca),dot2(cb)) );
        }
        float sdTorus( in vec3 p, in float r0, in float r1 ) {
            vec2 q = vec2(length(p.xz)-r0, p.y);
            return length(q)-r1;
        }
        float sdTriPrism( in vec3 p, in float h, in float r ) {
            vec3 q = abs(p);
            return max(q.z-h,max(q.x*0.866025+p.y*0.5,-p.y)-r*0.5);
        }
        float sdHexPrism( in vec3 p, in float h, in float r ) {
            const vec3 k = vec3(-0.8660254, 0.5, 0.57735);
            p = abs(p);
            p.xy -= 2.0*min(dot(k.xy, p.xy), 0.0)*k.xy;
            vec2 d = vec2(
                length(p.xy-vec2(clamp(p.x,-k.z*r,k.z*r), r))*sign(p.y-r),
                p.z-h );
            return min(max(d.x,d.y),0.0) + length(max(d,0.0));
        }
        float sdNgonPrism( in vec3 p, in float h, in float r, in float n) { // n: nsides
            const float PI = 3.14159;
        
            float theta, dist, side = n - 0.5, _h;
            vec2 a, b = vec2(r, 0), ba, pa;
            
            theta = (1.0 / n) * (2 * PI);
            a = b;
            b = vec2(r*cos(theta), r*sin(theta));
            
            ba = b-a;
            pa = p.xy-a;
            _h = clamp(dot(pa,ba)/dot(ba,ba),0.0,1.0);
            
            dist = length(pa-_h*ba);
            side -= sign((b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x));
            
            for (int i = 1; i < n; i++) {
                theta = ((i + 1) / n) * (2 * PI);
                a = b;
                b = vec2(r*cos(theta), r*sin(theta));
                
                ba = b-a;
                pa = p.xy-a;
                _h = clamp(dot(pa,ba)/dot(ba,ba),0.0,1.0);
                
                dist = min(length(pa-_h*ba),dist);
                side -= sign((b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x));
            }
            
            return opExtrusion(p, sign(side) * dist, h);
        }
'''

# A library of fragment shader
frag_include_ = '''
        struct SDFObjectProp {
            vec4 ps;  // position and scale
            vec4 qu;  // quaternion
            vec2 bl;  // blend
        };
        
        struct SDFBoxProp {
            vec4 br; // bound and round
        };
        
        struct SDfSphereProp {
            float r; // radius
        };
        
        struct SDFCylinderProp {
            float h;  // height
            float ra; // radius
            float rd; // round
            float dm; // dummy
        };
        
        struct SDFTorusProp {
            float r0; // radius 0
            float r1; // radius 1
        };
        
        struct SDFConeProp {
            float h;  // height
            float r0; // radius 0
            float r1; // radius 1
            float rd; // round
        };
        
        struct SDFPrismProp {
            float h;  // height
            float ra; // radius
            float rd; // round
            float dm; // dummy
        };
        
        struct SDFNgonPrismProp {
            float h;  // height
            float ra; // radius
            float rd; // round
            uint n;   // nsideds
        };
'''