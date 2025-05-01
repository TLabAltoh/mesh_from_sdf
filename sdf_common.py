# A library of distance functions and mathematical utilities.
include_ = '''
        mat4 rotmat(vec3 axis, float angle) {
            axis = normalize(axis);
            float s = sin(angle);
            float c = cos(angle);
            float oc = 1.0 - c;
            
            return mat4(oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
                        oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
                        oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
                        0.0,                                0.0,                                0.0,                                1.0);
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
        
        float opRoundUnion( in float d0, in float d1, in float radius )
        {
            vec2 u = max(vec2(radius - d0, radius - d1), vec2(0));
            return max(radius, min (d0, d1)) - length(u);
        }
        float opRoundDifference( in float d0, in float d1, in float radius )
        {
            return opRoundUnion(d0, -d1, radius);
        }
        float opRoundIntersection( in float d0, in float d1, in float radius )
        {
            vec2 u = max(vec2(radius + d0, radius + d1), vec2(0));
            return min(-radius, max (d0, d1)) + length(u);
        }

        float opChampferUnion( in float d0, in float d1, in float champferSize) {
            const float SQRT05 = 0.70710678118;
            return min(min(d0, d1), (d0 - champferSize + d1)*SQRT05);
        }
        float opChampferDifference( in float d0, in float d1, in float champferSize) {
            return opChampferUnion(d0, -d1, champferSize);
        }
        float opChampferIntersection( in float d0, in float d1, in float champferSize) {
            const float SQRT05 = 0.70710678118;
            return max(max(d0, d1), (d0 + champferSize + d1)*SQRT05);
        }
        
        float opStairsUnion( in float d0, in float d1, in float champferSize, in float n) {
            float s = champferSize/n;
            float u = d1-champferSize;
            return min(min(d0,d1), 0.5 * (u + d0 + abs ((mod (u - d0 + s, 2 * s)) - s)));
        }
        float opStairsDifference( in float d0, in float d1, in float champferSize, in float n) {
            return -opStairsUnion(-d0, d1, champferSize, n);
        }
        float opStairsIntersection( in float d0, in float d1, in float champferSize, in float n) {
            return -opStairsUnion(-d0, -d1, champferSize, n);
        }

        //
        // -----------------------------------------------------------------------------------------------


        float opExtrusion( in vec3 p, in float dist, in float height )
        {
            vec2 w = vec2( dist, abs(p.z) - height );
            return min(max(w.x,w.y),0.0) + length(max(w,0.0));
        }

        float sdBox( in vec3 p, in vec3 bounding, in float rounding ) {
            vec3 q = abs(p)-bounding+rounding;
            return length(max(q,0.0))+min(max(q.x,max(q.y,q.z)),0.0)-rounding;
        }
        float sdSphere( in vec3 p, in float radius ) {
            return length(p)-radius;
        }
        float sdCylinder( in vec3 p, in float height, in float radius )
        {
            vec2 d = abs(vec2(length(p.xz),p.y)) - vec2(radius,height);
            return min(max(d.x,d.y),0.0) + length(max(d,0.0));
        }
        float sdCappedCone( in vec3 p, in float h, in float r1, in float r2 )
        {
            vec2 q = vec2( length(p.xz), p.y );
            vec2 k1 = vec2(r2,h);
            vec2 k2 = vec2(r2-r1,2.0*h);
            vec2 ca = vec2(q.x-min(q.x,(q.y<0.0)?r1:r2), abs(q.y)-h);
            vec2 cb = q - k1 + k2*clamp( dot(k1-q,k2)/dot2(k2), 0.0, 1.0 );
            float s = (cb.x<0.0 && ca.y<0.0) ? -1.0 : 1.0;
            return s*sqrt( min(dot2(ca),dot2(cb)) );
        }
        float sdTorus( in vec3 p, in float radius0, in float radius1 ) {
            vec2 q = vec2(length(p.xz)-radius0, p.y);
            return length(q)-radius1;
        }
        float sdTriPrism( in vec3 p, in float radius0, in float radius1 ) {
            vec3 q = abs(p);
            return max(q.z-radius1,max(q.x*0.866025+p.y*0.5,-p.y)-radius0*0.5);
        }
        float sdHexPrism( in vec3 p, in vec2 h ) {
            const vec3 k = vec3(-0.8660254, 0.5, 0.57735);
            p = abs(p);
            p.xy -= 2.0*min(dot(k.xy, p.xy), 0.0)*k.xy;
            vec2 d = vec2(
                length(p.xy-vec2(clamp(p.x,-k.z*h.x,k.z*h.x), h.x))*sign(p.y-h.x),
                p.z-h.y );
            return min(max(d.x,d.y),0.0) + length(max(d,0.0));
        }
        float sdNgonPrism( in vec3 p, in float radius, in float nsides, in float height) {
            const float PI = 3.14159;
        
            float theta, dist, side = nsides - 0.5, h;
            vec2 a, b = vec2(radius, 0), ba, pa;
            
            theta = (1.0 / nsides) * (2 * PI);
            a = b;
            b = vec2(radius*cos(theta), radius*sin(theta));
            
            ba = b-a;
            pa = p.xy-a;
            h = clamp(dot(pa,ba)/dot(ba,ba),0.0,1.0);
            
            dist = length(pa-h*ba);
            side -= sign((b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x));
            
            for (int i = 1; i < nsides; i++) {
                theta = ((i + 1) / nsides) * (2 * PI);
                a = b;
                b = vec2(radius*cos(theta), radius*sin(theta));
                
                ba = b-a;
                pa = p.xy-a;
                h = clamp(dot(pa,ba)/dot(ba,ba),0.0,1.0);
                
                dist = min(length(pa-h*ba),dist);
                side -= sign((b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x));
            }
            
            return opExtrusion(p, sign(side) * dist, height);
        }
'''