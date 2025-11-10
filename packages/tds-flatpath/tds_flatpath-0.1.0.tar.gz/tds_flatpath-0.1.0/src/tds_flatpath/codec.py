import os
import re

# I created this to optimize file path flattening while providing an absolute collision proof guarnatee (not just statistical).
# My postfix trick keeps stems readable and only grows with the exact ambiguity you need to resolve (underscore runs + depth).
# Other comparable approaches give ground in either readability or length. Here are some examples:

# - escape-and-join: keeps one string but grows with every special char.
# - length-prefixed join: (e.g., `len:name`…) is reversible but far less readable.
# - Hashing: is compact and (statistically) safe but loses human readability and determinism across renames unless you keep a side index.

#TODO: possibly add an option to customize the join char (instead of hardcoding '_')

# Here are some possibilities for optimization to approach closer to SHA256 results: 
#       batch mode, precompute segments (for similar paths), table lookups

class TdsFlatNameCodecV1:
    """
    Collision-proof encoder using underscore-run postfix + depth separators.
    """

    VALID_POSTFIX_CHARS = set("n-0123456789ABCDEF")
    BENEFITS = "BENEFITS:\nOS-agnostic array input, deterministic, reversible, human readable, short `collision buckets` compared to a hash"

    # ---------- FLATTEN ---------- #
    @staticmethod
    def _postfix_from_segments(segments):
        """
        Construct the collision-proof postfix string from a sequence of path segments.

        Each segment is scanned in order:
          - For every consecutive run of '_' characters, append 'n' + HEX(count), uppercase.
          - After each segment (except the last), append a hyphen '-' to mark a directory boundary.
          - If no underscores are found in any segment, the postfix is a single '-'.

        The resulting string encodes both underscore density and directory depth,
        ensuring a deterministic, reversible mapping when combined with the flattened name.
        """
        parts = []
        for idx, seg in enumerate(segments):
            i = 0
            while i < len(seg):
                if seg[i] == "_":
                    j = i
                    while j < len(seg) and seg[j] == "_":
                        j += 1
                    parts.append("n" + format(j - i, "X"))
                    i = j
                else:
                    i += 1
            if idx < len(segments) - 1:
                parts.append("-")
        return "".join(parts) if parts else "-"

    @classmethod
    def flat_name(cls, path_array: list[str], validate: bool = True) -> str:
        if validate:
            if (not path_array) or any((not isinstance(s, str)) or (s == "") or (os.sep in s) for s in path_array):
                raise ValueError("Invalid path_array: non-empty strings only, no OS separators.")

        last = path_array[-1]
        name, ext = os.path.splitext(last)
        if not name and ext:
            name, ext = last, ""

        # Note if the file system (none that I know of) enforces the idea of extensions but doesn't allow an underscore
        # after the extension then you could do: f"{name}_{postfix}{ext}"
        if len(path_array) == 1:
            postfix = cls._postfix_from_segments([name])
            if postfix == "-":  # meaning no underscore sequences found
                return f"{name}{ext}"
            return f"{name}{ext}_{postfix}"

        dir_segs = path_array[:-1]
        flattened_stem = "_".join(dir_segs + [name])
        postfix = cls._postfix_from_segments(dir_segs + [name])
        return f"{flattened_stem}{ext}_{postfix}"


    # ---------------------------- BEGIN UNFLATTEN ---------------------------- #
    # EVERYTHING BELOW HERE CAN BE SAFELY REMOVED IF YOU DON'T NEED TO UNFLATTEN

    @classmethod
    # use this method if for some strange reason you have file 'extensions' that don't allow underscores after them
    # you would ned to chage `flat_name` appropriately. I am only providing this just for educational purposes
    def split_base_postfix_ext(cls, filename: str):
        i = filename.rfind("_")
        base, tail = (filename[:i], filename[i+1:]) if i != -1 else (filename, "")
        j = 0
        valid = TdsFlatNameCodecV1.VALID_POSTFIX_CHARS
        while j < len(tail) and tail[j] in valid:
            j += 1
        return base, tail[:j], tail[j:]  # base, postfix, ext
    
    @classmethod
    # TODO: see if this can be more concise. add some validation
    def split_base_ext_postfix(cls, filename: str):
        # Locate the underscore that begins the postfix
        u = filename.rfind("_")
        if u == -1:
            # No postfix at all. Split extension normally
            dot = filename.rfind(".")
            if dot == -1:
                return filename, "", ""
            return filename[:dot], filename[dot:], ""

        # Everything after that underscore is postfix
        postfix = filename[u+1:]   # DROP the underscore

        # Everything before that underscore is (<base><ext>)
        prefix = filename[:u]

        # Now split extension inside prefix
        dot = prefix.rfind(".")
        if dot == -1:
            # No extension
            return prefix, "", postfix

        base = prefix[:dot]
        ext = prefix[dot:]          # includes leading '.'
        return base, ext, postfix



    @classmethod
    def postfix_to_counts(cls,postfix: str):
        """
        Convert postfix into array of integers:
        - 'n<HEX>' becomes that integer
        - '-' becomes 0 (directory separator)
        Example: 'n1-n1-n2' -> [1, 1, 0, 2]
        """
        parts = re.split(r'(n|-)', postfix)
        counts = []
        it = iter(parts)

        for p in it:
            if not p:
                continue
            if p == '-':
                counts.append(0)
            elif p == 'n':
                hexpart = next(it)
                counts.append(int(hexpart, 16))
            else:
                # standalone hex run (only occurs when no leading 'n' needed)
                counts.append(int(p, 16))

        return counts

    @classmethod
    def unflatten_to_path(cls, flattened_filename):
        """
        Reverse of flat_name: returns list of original path segments.
        """
        # you would use this approach if you had {base}_{postfix}{ext} structure and 
        # base, postfix, ext = cls.split_base_postfix_ext(flattened_filename)
        base, ext, postfix = cls.split_base_ext_postfix(flattened_filename)
        counts = cls.postfix_to_counts(postfix)

        i = 0          # cursor into base
        cur = []       # chars for current segment
        path = []      # completed segments (last one will get ext)

        for c in counts:
            if c == 0:
                # Directory boundary: take letters up to the next '_' (if any),
                # then skip exactly that one '_' which was used as the separator.
                j = base.find("_", i)
                if j == -1:
                    # Sentinel '-' case: no underscores left at all → boundary at end
                    path.append("".join(cur))
                    cur = []
                    i = len(base)
                else:
                    cur.append(base[i:j])
                    i = j + 1  # skip the separator underscore
                    path.append("".join(cur))
                    cur = []
            else:
                # We need to consume exactly c underscores INTO the current segment.
                # If we're not at an underscore yet, slurp letters until we reach one.
                while i < len(base) and base[i] != "_":
                    cur.append(base[i])
                    i += 1

                # Now take exactly c underscores.
                if base[i:i+c] != "_" * c:
                    raise ValueError("Malformed flattened string vs postfix: underscore run mismatch.")
                cur.append(base[i:i+c])
                i += c

        # Whatever remains in the base belongs to the final segment's stem
        cur.append(base[i:])
        path.append("".join(cur) + ext)
        return path
    # ----------------------------- END UNFLATTEN ----------------------------- #