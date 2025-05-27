
class Algorithm(object):

    # Utility classes for using sorting algorithms, etc.
    
    @classmethod
    def __quick_sort_by_index(cls, alist, l, r):
        # https://zenn.dev/yutabeee/articles/e8fb2847cfc980
        
        i = l
        j = r
        p = (l + r) // 2
        
        while True:
            while alist[i].object.sdf_prop.index < alist[p].object.sdf_prop.index:
                i = i + 1
            while alist[j].object.sdf_prop.index > alist[p].object.sdf_prop.index:
                j = j - 1
                
            if i >= j:
                break
            
            alist.move(i,j)
            
            if l < i - 1:
                cls.__quick_sort_by_index(alist, l, i - 1)
            if r > j + 1:
                cls.__quick_sort_by_index(alist, j + 1, r)
    
    @classmethod
    def quick_sort_by_index(cls, alist):
        # Algorithms.quick_sort_by_index(cls, alist)
        if len(alist) == 0:
            return;
        cls.__quick_sort_by_index(alist, 0, len(alist) - 1)