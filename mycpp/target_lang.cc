// Target Language Constructs
//
// We're generating a subset of C++.
//
// - Done:
//   - initializer lists
//   - exceptions
//   - default arguments
//   - namespaces
//
// - advanced:
//   - What do Python closures get translated to?  Oil uses them in a few
//     places, e.g. for the readline callbacks.
//   - C++ 20 coroutines (but we're almost certainly not using this)

#include <stdarg.h>  // va_list, etc.
#include <stdio.h>   // vprintf

#include <initializer_list>
#include <memory>  // shared_ptr
#include <unordered_map>
#include <vector>

#include <stdexcept>

#include "dumb_alloc.h"
#include "greatest.h"

using std::unordered_map;

void log(const char* fmt, ...) {
  va_list args;
  va_start(args, fmt);
  vprintf(fmt, args);
  va_end(args);
  printf("\n");
}

class List {
 public:
  List(std::initializer_list<int> init) : v_() {
    for (int i : init) {
      v_.push_back(i);
    }
  }
  std::vector<int> v_;
};

template <class T>
class Array {
 public:
  Array() : v_() {
  }

  Array(std::initializer_list<T> init) : v_() {
    for (T i : init) {
      v_.push_back(i);
    }
  }

  void append(T item) {
    v_.push_back(item);
  }

  int size() {
    return v_.size();
  }

  std::vector<T> v_;
};

class FatalError {};

class ParseError : public FatalError {
 public:
  ParseError(const char* reason) : reason_(reason) {
  }
  const char* reason() const {
    return reason_;
  }

 private:
  const char* reason_;
};

// https://stackoverflow.com/questions/8480640/how-to-throw-a-c-exception
int compare(int a, int b) {
  if (a < 0 || b < 0) {
    throw std::invalid_argument("received negative value");
  }
  return a < b;
}

int parse(const char* text) {
  if (text[0] == 'f') {
    throw ParseError("started with f");
  }
  return 0;
}

void throw_fatal() {
  throw FatalError();
}

void except_subclass_demo() {
  try {
    throw_fatal();
    // parse("f");
  } catch (ParseError& e) {
    // Doesn't get caught.  Does this rely on RTTI, or is it static?
    // I think it's static but increases the size of the exception table.
    log("Got ParseError: %s", e.reason());
  }
}

TEST except_demo() {
  int num_caught = 0;

  log("compare(3, 1): %d", compare(1, 3));
  log("compare(5, 4): %d", compare(5, 4));

  try {
    log("compare(-1, 3): %d", compare(-1, 3));
  } catch (const std::invalid_argument& e) {
    log("Got exception: %s", e.what());
    num_caught++;
  }

  log("");

  try {
    log("parse('foo'): %d", parse("foo"));
  } catch (const ParseError& e) {
    log("Got exception: %s", e.reason());
    num_caught++;
  }

  try {
    log("parse('bar'): %d", parse("bar"));
  } catch (const ParseError& e) {
    log("Got exception: %s", e.reason());
    num_caught++;  // we don't get here
  }

  try {
    except_subclass_demo();
  } catch (const FatalError& e) {
    log("Got FatalError");
    num_caught++;
  }

  ASSERT_EQ_FMT(3, num_caught, "%d");

  PASS();
}

TEST template_demo() {
  Array<int> a;
  a.append(1);
  a.append(2);
  a.append(3);
  log("a.size() = %d", a.size());

  Array<List*> a2;
  a2.append(new List{1, 2, 3});
  a2.append(new List{4, 5, 6});
  log("a2.size() = %d", a2.size());

  PASS();
}

void f(int a, int b = -1, const char* s = nullptr) {
  log("");
  log("a = %d", a);
  log("b = %d", b);
  log("s = %p", s);
}

TEST default_args_demo() {
  f(42, 43, "foo");
  f(42, 43);
  f(42);

  PASS();
}

namespace core {
namespace util {
void p_die(const char* s) {
  log("p_die %s", s);
}
}  // namespace util
}  // namespace core

namespace tdop {
using core::util::p_die;

class Parser {
 public:
  Parser(int token) : token_(token) {
    log("Parser %d", token);
    p_die("Parser");
  }
  int token_;
};
}  // namespace tdop

namespace typed_arith_parse {
// using namespace core;  This makes EVERYTHING available.

namespace util = core::util;

// This lets us use "Parser""
using tdop::Parser;

TEST namespace_demo() {
  log("");
  log("namespace_demo()");
  f(42);
  auto p = new tdop::Parser(42);
  auto p2 = new Parser(43);

  util::p_die("ns");

  PASS();
}
}  // namespace typed_arith_parse

// Conclusion: every Python module should have is own namespace
//
// from core.util import log => using core::util::log
// from core import util => namespace util = core::util;

// test out the size of 5 uint16_t.  OK it's actually padded, which is nice!
// Because there is no big element.
struct Extent {
  uint16_t s_line_id;
  uint16_t s_col;
  uint16_t e_line_id;
  uint16_t e_col;
  uint16_t src_id;
};

class expr__Const {
 public:
  expr__Const(int i) : i_(i) {
  }
  int i_;
};

namespace expr {
typedef expr__Const Const;
}

using std::shared_ptr;

shared_ptr<expr__Const> f(shared_ptr<expr__Const> arg) {
  return shared_ptr<expr__Const>(new expr__Const(arg->i_ + 10));
}

TEST shared_ptr_demo() {
  std::shared_ptr<expr__Const> e = std::make_shared<expr__Const>(5);
  log("e->i_ = %d", e->i_);
  // 16, not 24?
  // These are contiguous.
  log("sizeof(e) = %zu", sizeof(e));

  std::shared_ptr<expr__Const> e2(new expr__Const(7));
  log("e2->i_ = %d", e2->i_);
  log("sizeof(e2) = %zu", sizeof(e2));

  std::shared_ptr<expr__Const> e3 = f(e2);

  log("e3->i_ = %d", e3->i_);
  log("sizeof(e3) = %zu", sizeof(e3));

  PASS();
}

TEST map_demo() {
  unordered_map<int, int> m;
  log("m.size = %d", m.size());

  // Hm integers have a hash function
  m[3] = 4;
  m[5] = 9;
  log("m.size = %d", m.size());

  // Hm you always get the pairs
  // Should this be const auto& or something?
  for (auto item : m) {
    log("iterating %d %d", item.first, item.second);
  }

  log("---");

  unordered_map<Extent*, int> m2;
  log("m2.size = %d", m2.size());

  // hm do I want this operator overloading?
  m2[nullptr] = 42;
  log("m2.size = %d", m2.size());

  log("retrieved = %d", m2[nullptr]);

  PASS();
}

TEST sizeof_demo() {
  log("sizeof(int): %d", sizeof(int));
  log("sizeof(int*): %d", sizeof(int*));
  log("sizeof(Extent): %d", sizeof(Extent));
  log("");

  // Good, this is 50.
  Extent ext_array[5];
  log("sizeof(ext_array): %d", sizeof(ext_array));
}

TEST test_misc() {
  List l{1, 2, 3};
  log("size: %d", l.v_.size());
  log("");

  // Dict literal syntax?
  // Dict d {{"key", 1}, {"val", 2}};

  log("");
  expr::Const c(42);
  log("expr::Const = %d", c.i_);

  dumb_alloc::Summarize();

  PASS();
}

struct Point {
  int x;
  int y;
};

// structs don't have any constructors, so don't need any constexpr stuff
constexpr Point p = {3, 4};

// members must be public to allow initializer list
class PointC {
 public:
  // constructor is allowed
  // needs to be constexpr
  constexpr PointC(int x, int y) : x_(x), y_(y) {
  }
  // this is allowed too
  int get_x() {
    return x_;
  }
  // this is allowed too
  virtual int mag() const {
    return x_ * x_ + y_ * y_;
  }

  int x_;
  int y_;
};

constexpr PointC pc = {5, 6};

class SubPointC : public PointC {
 public:
  constexpr SubPointC(int x, int y) : PointC(x, y) {
  }
  virtual int mag() const {
    return 0;
  }
};

constexpr SubPointC sub = {7, 8};

class Compound {
 public:
  PointC c1;
  PointC c2;
};

// This works, but what about pointers?
constexpr Compound c = {{0, 1}, {8, 9}};

TEST static_literals() {
  ASSERT_EQ(3, p.x);
  ASSERT_EQ(4, p.y);

  ASSERT_EQ(5, pc.x_);
  ASSERT_EQ(6, pc.y_);

  // I'm surprised virtual functions are allowed!  We're compiling with
  // -std=c++11.
  // But this is just curiosity.  We don't need this in ASDL.
  ASSERT_EQ_FMT(61, pc.mag(), "%d");

  ASSERT_EQ_FMT(0, sub.mag(), "%d");

  ASSERT_EQ(0, c.c1.x_);
  ASSERT_EQ(1, c.c1.y_);
  ASSERT_EQ(8, c.c2.x_);
  ASSERT_EQ(9, c.c2.y_);

  PASS();
}

enum class Color_e { red, blue };

TEST enum_demo() {
  Color_e c1 = Color_e::red;
  Color_e c2 = Color_e::blue;
  int array[2] = {3, 4};

  // You can cast these strong enums to an integer.  We don't do that in the
  // MyPy source, but maybe we could?  It's kind of a pain though.

  log("c1 %d", static_cast<int>(c1));
  log("c2 %d", static_cast<int>(c2));

  log("array[c1] %d", array[static_cast<int>(c1)]);
}

GREATEST_MAIN_DEFS();

int main(int argc, char** argv) {
  GREATEST_MAIN_BEGIN();

  RUN_TEST(typed_arith_parse::namespace_demo);

  RUN_TEST(test_misc);
  RUN_TEST(map_demo);
  RUN_TEST(shared_ptr_demo);
  RUN_TEST(template_demo);
  RUN_TEST(default_args_demo);
  RUN_TEST(sizeof_demo);
  RUN_TEST(except_demo);
  RUN_TEST(static_literals);
  RUN_TEST(enum_demo);

  GREATEST_MAIN_END(); /* display results */
  return 0;
}
