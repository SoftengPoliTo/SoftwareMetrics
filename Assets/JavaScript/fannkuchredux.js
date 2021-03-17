/* The Computer Language Benchmarks Game
   http://benchmarksgame.alioth.debian.org/

   contributed by Isaac Gouy, transliterated from Mike Pall's Lua program 
   modified by Roman Pletnev
*/

const fannkuch = n => {
   const p = new Int32Array(n), q = new Int32Array(n), s = new Int32Array(n);
   let sign = 1, maxflips = 0, sum = 0, m = n - 1;
   for (let i = 0; i < n; i++) {
      p[i] = i;
      q[i] = i;
      s[i] = i;
   }
   while (true) {
      // Copy and flip.
      let q0 = p[0];                                     // Cache 0th element.
      if (q0 !== 0) {
         for(let i = 1; i < n; i++)
            q[i] = p[i];                                 // Work on a copy.
         let flips = 1;
         while (true) {
            if (q[q0] === 0) {                           // ... until 0th element is 0.
               sum += sign * flips;
	            if (flips > maxflips)
                  maxflips = flips;                      // New maximum?
               break; 
            } 
            q[q0] = q0;
            if (q0 >= 3) {
               let i = 1, j = q0 - 1;
               do {
                  [q[i], q[j]] = [q[j], q[i]];
                  i++;
                  j--;
               }
               while (i < j);
            }
            q0 = qq;
            flips++;
         }
      }
      // Permute.
      if (sign === 1) {
         [p[1], p[0]] = [p[0], p[1]];
         sign--;
      }
      else {
         [p[1], p[2]] = [p[2], p[1]];
         sign = 1;
         for (let i = 2; i < n; i++) {
            if (s[i] !== 0) {
               s[i] = s[i] - 1;
               break;
            }
            if (i === m)
               return [sum, maxflips];                   // Out of permutations.
            s[i] = i;
            // Rotate 0<-...<-i+1.
            q0 = p[0];
            for (let j = 0; j <= i; j++)
               p[j] = p[j + 1];
            p[i + 1] = q0;
         }
      }
   }
};

const n = +process.argv[2];
const [zero, one] = fannkuch(n);
console.log(`${zero}\nPfannkuchen(${n}) = ${one}`);
