#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

namespace {
 // Important
  struct Hello : public FunctionPass {
    static char ID;
    Hello() : FunctionPass(ID) {}
 // Important
    bool runOnFunction(Function &F) override {
      errs() << "Hello: ";
      errs().write_escaped(F.getName()) << '\n';
      return false;
    }
  };
}

char Hello::ID = 0;

// Important:Register for opt
static RegisterPass<Hello> X("hello", "Hello World Pass");

// Important:Register for clang
static RegisterStandardPasses Y(PassManagerBuilder::EP_EarlyAsPossible,
  [](const PassManagerBuilder &Builder, legacy::PassManagerBase &PM) {
    PM.add(new Hello());
  });