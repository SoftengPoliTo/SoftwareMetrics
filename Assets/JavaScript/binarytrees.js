/* The Computer Language Benchmarks Game
   http://benchmarksgame.alioth.debian.org/
   contributed by Isaac Gouy 
   *reset* 
*/

class TreeNode {
   constructor(left, right) {
      this.left = left;
      this.right = right;
   }

   itemCheck() {
      const {left, right} = this;
      return 1 + (left === null ? 0 : (left.itemCheck() + right.itemCheck()));
   }
}

const bottomUpTree = depth => {
   const lr = depth > 0 ? bottomUpTree(depth - 1) : null;
   return new TreeNode(lr, lr);
};

const minDepth = 4;
const n = +process.argv[2];
const maxDepth = Math.max(minDepth + 2, n);
const stretchDepth = maxDepth + 1;

let check = bottomUpTree(stretchDepth).itemCheck();
console.log(`stretch tree of depth ${stretchDepth}\t check: ${check}`);

const longLivedTree = bottomUpTree(maxDepth);
for (let depth = minDepth; depth <= maxDepth; depth += 2) {
   const iterations = 1 << (maxDepth - depth + minDepth);
   check = 0;
   for (let i = 1; i <= iterations; i++)
      check += bottomUpTree(depth).itemCheck();
   console.log(`${iterations}\t trees of depth ${depth}\t check: ${check}`);
}

check = longLivedTree.itemCheck();
console.log(`long lived tree of depth ${maxDepth}\t check: ${check}`);
